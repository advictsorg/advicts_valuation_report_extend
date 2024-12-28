from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    avg_cost = fields.Float(string='AVG Cost', compute='_compute_avg_cost')
    purchase_cost = fields.Float(string='PO Cost', compute='_compute_purchase_cost')
    landed_cost = fields.Float(string='Landed Cost', compute='_compute_landed_cost')
    landed_cost_per_unit = fields.Float(string='Landed Cost Per Unit', compute='_compute_landed_cost_per_unit')

    def _compute_avg_cost(self):
        for rec in self:
            # Get all valuation layers for this product before current layer's date
            domain = [
                ('product_id', '=', rec.product_id.id),
                ('create_date', '<=', rec.create_date),
                ('stock_move_id.state', '=', 'done'),
            ]

            layers = self.env['stock.valuation.layer'].search(domain)

            if layers:
                total_quantity = sum(layer.quantity for layer in layers)
                total_value = sum(layer.value for layer in layers)

                if total_quantity != 0:
                    rec.avg_cost = abs(total_value / total_quantity)
                else:
                    rec.avg_cost = rec.product_id.standard_price
            else:
                rec.avg_cost = rec.product_id.standard_price

    def _compute_purchase_cost(self):
        for rec in self:
            if rec.stock_move_id:
                if rec.stock_move_id.purchase_line_id:
                    rec.purchase_cost = rec.stock_move_id.purchase_line_id.price_unit
                else:
                    rec.purchase_cost = 0.0
            else:
                rec.purchase_cost = 0.0

    def _compute_landed_cost(self):
        for rec in self:
            domain = [('stock_landed_cost_id', '!=', False),
                      ('product_id', '=', rec.product_id.id),
                      ('create_date', '<=', rec.create_date), ]
            layers = self.env['stock.valuation.layer'].search(domain)

            if layers:
                rec.landed_cost = sum(layer.value for layer in layers)
            else:
                rec.landed_cost = 0.0

    def _compute_landed_cost_per_unit(self):
        for rec in self:
            domain = [('stock_landed_cost_id', '!=', False),
                      ('product_id', '=', rec.product_id.id),
                      ('create_date', '<=', rec.create_date), ]
            layers = self.env['stock.valuation.layer'].search(domain)

            if layers:
                total_landed_cost = sum(layer.value for layer in layers)
                total_quantity = sum(layer.stock_valuation_layer_id.quantity for layer in layers)
                rec.landed_cost_per_unit = total_landed_cost / total_quantity
            else:
                rec.landed_cost_per_unit = 0.0
