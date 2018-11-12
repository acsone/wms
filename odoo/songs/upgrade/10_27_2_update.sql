UPDATE
   ir_model_data
SET
   noupdate = false
WHERE module='specific_helpdesk'
AND model='helpdesk.ticket.reason'
;
