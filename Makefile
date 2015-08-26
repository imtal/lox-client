# Wrapper around Python setuptools
#SHELL=bash
DESTDIR=/usr/lib
LANGUAGES=nl fy
DOMAIN=lox-client
PO_FILES=$(foreach lang,$(LANGUAGES),po/$(lang).po)
MO_FILES=$(foreach lang,$(LANGUAGES),build/locale/$(lang)/LC_MESSAGES/$(DOMAIN).mo)

all: $(MO_FILES)
	python setup.py build

clean:
	find . -name "*.pyc" -type f -delete

po/$(DOMAIN).pot:
	@echo create po template
	@xgettext -L Python -d $(DOMAIN) -o po/$(DOMAIN).pot `find . -name "*.py"`
	@#python setup.py extract_messages --verbose --output-file po/$(DOMAIN).pot --charset utf-8 --input-dirs ./lox

$(PO_FILES): po/lox-client.pot
ifeq ("$(wildcard po/$@)","")
	@echo create $@
	@msginit --no-translator -i po/$(DOMAIN).pot -o $@
	@#python setup.py init_catalog --locale $(notdir $(basename $@)) --input-file po/lox-client.pot --output-file $@
else
	@echo merge $@
	@msgmerge -U $@ po/$(DOMAIN).pot
	@#python setup.py update_catalog ...
endif

build/locale/%/LC_MESSAGES/$(DOMAIN).mo: po/%.po
	@mkdir -p $(dir $@)
	@echo creating $@
	@msgfmt --statistics $< -o $@

install:
	python setup.py install

uninstall:
	rm -rf /usr/local/lib/python2.7/dist-packages/lox_client-0.1-py2.7.egg
	rm -f /usr/local/bin/lox-client
	rm -f /usr/share/applications/lox-client.desktop
	rm -f /usr/share/icons/localbox.png
	rm -f /usr/share/locale/*/LC_MESSAGES/lox-client.mo

