# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import re as regex
import subprocess as subprocess
from subprocess import CalledProcessError

class zlua(kp.Plugin):
    """
    Z for LUA plugin

    Z: https://github.com/skywind3000/z.lua
    """

    _debug = True

    def __init__(self):
        super().__init__()

    def on_start(self):
        pass

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category = kp.ItemCategory.KEYWORD,
                label = "Z",
                short_desc = "Z for LUA",
                target = "Z",
                args_hint = kp.ItemArgsHint.REQUIRED,   # the item can't be executed directly but needs more arguments
                hit_hint = kp.ItemHitHint.KEEPALL       # the item and the selected argument will be tracked in history
            )
        ])

    def on_suggest(self, user_input, items_chain):
        # Don't add suggestion items if items_chain is empty
        # (Z catalog item was not yet selected)
        if not items_chain:
            return

        suggestion_items = self.get_z_suggestions(user_input)

        self.set_suggestions(suggestion_items, match_method=kp.Match.ANY, sort_method=kp.Sort.NONE)

    def on_execute(self, item, action):
        path = item.target()
        kpu.explore_file(path)

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        pass

    def get_z_suggestions(self, user_input):
        suggestion_items = []
        try:
            result = subprocess.check_output(
                'z -l ' + user_input, 
                shell=True, 
                encoding='utf-8',
                universal_newlines=True
            )

            result = result.replace('\r', '')
            lines = result.split('\n')

            for line in lines:
                elements = line.split('       ')
                if len(elements) > 1:
                    frecency = elements[0]
                    path = elements[1].strip()

                    path_elements = path.split('\\')

                    self.dbg(path)

                    suggestion_items.append(self.create_item(
                        category=kp.ItemCategory.FILE,
                        label=path_elements[-1],
                        short_desc='',
                        target=path,
                        args_hint=kp.ItemArgsHint.ACCEPTED,
                        hit_hint=kp.ItemHitHint.IGNORE,
                    ))

            return list(reversed(suggestion_items))

        except CalledProcessError as e:
            suggestion_items.append(self.create_error_item(
                label="CalledProcessError",
                short_desc=e.returncode,
            ))

        return suggestion_items