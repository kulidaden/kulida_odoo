from odoo import models,fields, Command
import logging


class EstateAccount(models.Model):
    _inherit = 'estate.property'

    account_move_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    _logger = logging.getLogger(__name__)

    def action_sold_(self):
        super().action_sold_()

        self._logger.info('Creating invoice for property %s', self.name)

        if not self.buyer_id:
            raise models.ValidationError("No buyer assigned to this property!")

        commission_amount = self.selling_price * 0.06

        invoice_vals={
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                Command.create({
                    'name':'Commission(6%)',
                    'quantity':1,
                    'price_unit': commission_amount,
                }),
                Command.create({
                    'name': 'Administrative Fees',
                    'quantity': 1,
                    'price_unit': 100.00,
                }),
            ],
        }

        account_move=self.env['account.move'].create(invoice_vals)

        self.account_move_id=account_move.id

