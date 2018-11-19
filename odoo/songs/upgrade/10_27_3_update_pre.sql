-- delete ir.cron so it gets recreated by module update
DELETE FROM ir_cron WHERE id = (SELECT res_id FROM ir_model_data WHERE module = 'connector_esb' AND name = 'ir_cron_esb_export_document_zip');
DELETE FROM ir_model_data WHERE module = 'connector_esb' AND name = 'ir_cron_esb_export_document_zip';
