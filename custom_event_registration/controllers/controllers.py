# -*- coding: utf-8 -*-

import werkzeug
from werkzeug.exceptions import NotFound
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerCustom(WebsiteEventController):

    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''], type='http', auth="public",
                methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        registrations = self._process_attendees_form(event, post)
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
        contacts = request.env['res.partner'].sudo().search([])
        leads = request.env['crm.lead'].sudo().search([])
        for contact in contacts:
            if registrations[0]['email'] == contact['email'] and registrations[0]['phone'] == contact['phone']:
                continue
            elif registrations[0]['phone'] == contact['phone']:
                contact.write({'email': registrations[0]['email']})
                continue
            elif registrations[0]['email'] == contact['email']:
                print('I wroooote the phone')
                contact.write({'phone': registrations[0]['phone']})
                continue
        for lead in leads:
            if lead['phone'] and lead['email_from']:
                if registrations[0]['email'] == lead['email_from'] and registrations[0]['phone'] == lead['phone']:
                    lead.unlink()
                    contacts.create({
                        'name': registrations[0]['name'],
                        'email': registrations[0]['email'],
                        'phone': registrations[0]['email']})
                    continue
            if lead['email_from'] and not lead['phone']:
                if registrations[0]['email'] == lead['email_from']:
                    lead.unlink()
                    contacts.create({
                        'name': registrations[0]['name'],
                        'email': registrations[0]['email']})
                    continue
            if lead['phone'] and not lead['email_from']:
                if registrations[0]['phone'] == lead['phone']:
                    lead.unlink()
                    contacts.create({
                        'name': registrations[0]['name'],
                        'phone': registrations[0]['phone']})
                    continue

        return request.render("website_event.registration_complete",
                              self._get_registration_confirm_values(event, attendees_sudo))
