# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.terminal import TerminalBase


class TerminalModule(TerminalBase):

    terminal_stdout_re = [
        re.compile(
            rb".*[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?.*"
        ),
        # re.compile(br"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?$"),
        re.compile(rb"Finished downloading public key file!"),
    ]

    terminal_stderr_re = [
        re.compile(rb"% ?Error"),
        re.compile(rb"% ?Bad secret"),
        re.compile(rb"[\r\n%] Bad passwords"),
        re.compile(rb"invalid input", re.I),
        re.compile(rb"(?:incomplete|ambiguous) command", re.I),
        re.compile(rb"connection timed out", re.I),
        re.compile(rb"[^\r\n]+ not found"),
        re.compile(rb"'[^']' +returned error code: ?\d+"),
        re.compile(rb"Bad mask", re.I),
        re.compile(rb"% ?(\S+) ?overlaps with ?(\S+)", re.I),
        re.compile(rb"[%\S] ?Error: ?[\s]+", re.I),
        re.compile(rb"[%\S] ?Informational: ?[\s]+", re.I),
        re.compile(rb"Command authorization failed"),
        re.compile(rb"Error - *"),
        re.compile(rb"Error - Incorrect username or password."),
        re.compile(rb"Invalid input"),
        re.compile(rb"Already a http operation is in progress"),
        re.compile(rb"Flash access in progress. Please try later"),
        re.compile(rb"SSH tftp client public key failed!"),
        re.compile(rb"Error: .*"),
        re.compile(rb"^Error: .*", re.I),
        re.compile(rb"Error:.*"),
        re.compile(rb"Error:.*", re.I),
        re.compile(rb"^Ambiguous input"),
        re.compile(rb"Errno"),
    ]

    def on_open_shell(self):
        self.on_become(passwd=self._connection._play_context.password)
        try:
            self._exec_cli_command(b"skip")
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure("unable to set terminal parameters")

    def __del__(self):
        try:
            self._connection.close()
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure("unable to set terminal parameters")

    def on_become(self, passwd=None):
        if self._get_prompt().endswith(b"#"):
            return

        cmd = {"command": "enable"}
        cmd["prompt"] = to_text(
            r"[\r\n](?:Local_)?[Pp]assword: ?$", errors="surrogate_or_strict"
        )
        cmd["answer"] = passwd
        cmd["prompt_retry_check"] = True
        try:
            self._exec_cli_command(
                to_bytes(json.dumps(cmd), errors="surrogate_or_strict")
            )
            prompt = self._get_prompt()
            if prompt is None or not prompt.endswith(b"#"):
                raise AnsibleConnectionFailure(
                    "failed to elevate privilege to enable mode still at prompt [%s]"
                    % prompt
                )
        except AnsibleConnectionFailure as e:
            prompt = self._get_prompt()
            raise AnsibleConnectionFailure(
                "unable to elevate privilege to enable mode, at prompt [%s] with error: %s"
                % (prompt, e.message)
            )

    def on_unbecome(self):
        prompt = self._get_prompt()
        if prompt is None:
            return

        if b"(config" in prompt:
            self._exec_cli_command(b"exit")

        elif prompt.endswith(b"#"):
            self._exec_cli_command(b"exit")
