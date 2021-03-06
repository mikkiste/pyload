# -*- coding: utf-8 -*-
#
# Test links:
# http://uploadhero.co/dl/wQBRAVSM

import re

from module.plugins.internal.SimpleHoster import SimpleHoster, create_getInfo


class UploadheroCom(SimpleHoster):
    __name__    = "UploadheroCom"
    __type__    = "hoster"
    __version__ = "0.17"

    __pattern__ = r'http://(?:www\.)?uploadhero\.com?/dl/\w+'

    __description__ = """UploadHero.co plugin"""
    __license__     = "GPLv3"
    __authors__     = [("mcmyst", "mcmyst@hotmail.fr"),
                       ("zoidberg", "zoidberg@mujmail.cz")]


    NAME_PATTERN    = r'<div class="nom_de_fichier">(?P<N>.*?)</div>'
    SIZE_PATTERN    = r'Taille du fichier : </span><strong>(?P<S>.*?)</strong>'
    OFFLINE_PATTERN = r'<p class="titre_dl_2">|<div class="raison"><strong>Le lien du fichier ci-dessus n\'existe plus.'

    COOKIES = [("uploadhero.co", "lang", "en")]

    IP_BLOCKED_PATTERN = r'href="(/lightbox_block_download\.php\?min=.*?)"'
    IP_WAIT_PATTERN    = r'<span id="minutes">(\d+)</span>.*\s*<span id="seconds">(\d+)</span>'

    CAPTCHA_PATTERN = r'"(/captchadl\.php\?\w+)"'

    LINK_FREE_PATTERN    = r'var magicomfg = \'<a href="(http://[^<>"]*?)"|"(http://storage\d+\.uploadhero\.co/\?d=\w+/[^<>"/]+)"'
    LINK_PREMIUM_PATTERN = r'<a href="(.+?)" id="downloadnow"'


    def handleFree(self, pyfile):
        self.checkErrors()

        m = re.search(self.CAPTCHA_PATTERN, self.html)
        if m is None:
            self.error(_("CAPTCHA_PATTERN not found"))
        captcha_url = "http://uploadhero.co" + m.group(1)

        for _i in xrange(5):
            captcha = self.decryptCaptcha(captcha_url)
            self.html = self.load(pyfile.url, get={"code": captcha})
            m = re.search(self.LINK_FREE_PATTERN, self.html)
            if m:
                self.correctCaptcha()
                download_url = m.group(1) or m.group(2)
                break
            else:
                self.invalidCaptcha()
        else:
            self.fail(_("No valid captcha code entered"))

        self.download(download_url)


    def checkErrors(self):
        m = re.search(self.IP_BLOCKED_PATTERN, self.html)
        if m:
            self.html = self.load("http://uploadhero.co" + m.group(1))

            m = re.search(self.IP_WAIT_PATTERN, self.html)
            wait_time = (int(m.group(1)) * 60 + int(m.group(2))) if m else 5 * 60
            self.wait(wait_time, True)
            self.retry()

        self.info.pop('error', None)


getInfo = create_getInfo(UploadheroCom)
