.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

FACEBOOK_RAW?=./data/raw/Facebook/messages.htm
FACEBOOK?=./data/interim/Facebook/
DIGSBY?="./data/raw/Digsby Logs"
TRILLIAN?="./data/raw/Trillian"
PIDGIN?="./data/raw/Pidgin"
YAHOO?="./data/raw/Yahoo"
WHATSAPP?="./data/raw/Whatsapp"
SQLITE?="./data/interim/messages.db"

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -r requirements.txt

$(FACEBOOK): $(FACEBOOK_RAW)
	python src/data/fb_cleaner.py $(FACEBOOK_RAW) "$(FACEBOOK)cleaned.html"

$(SQLITE): facebook_clean
	python src/data/sqlite_importer.py --facebook_path $(FACEBOOK) \
		--trillian_path $(TRILLIAN) --pidgin_path $(PIDGIN) \
		--digsby_path $(DIGSBY) --whatsapp_path $(WHATSAPP) $(SQLITE)

clean:
	find . -name "*.pyc" -exec rm {} \;

clean_sqlite:
	python src/data/sqlite_importer.py --drop_table $(SQLITE)

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################
facebook_clean: $(FACEBOOK)
sqlite_import: $(SQLITE)
