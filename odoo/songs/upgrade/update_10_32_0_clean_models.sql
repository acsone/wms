-- We have some models in ir.model which have
-- been dropped from the code. Clean them
DELETE FROM ir_model_constraint
WHERE model IN (
  SELECT id FROM ir_model
  WHERE model IN (
  'db2.importer',
  'db2.importer.table',
  'report.stock.quant.bylocation.reserve',
  'stock.wizard.reassort',
  'round.instance.picking.state',
  'change.lot',
  'change.lot.line'
));
DELETE FROM ir_model
WHERE model IN (
    'db2.importer',
    'db2.importer.table',
    'report.stock.quant.bylocation.reserve',
    'stock.wizard.reassort',
    'round.instance.picking.state',
    'change.lot',
    'change.lot.line'
);
