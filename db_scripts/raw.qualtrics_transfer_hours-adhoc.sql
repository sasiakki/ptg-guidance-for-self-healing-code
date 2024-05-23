ALTER TABLE raw.qualtrics_transfer_hours
ADD COLUMN recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP;