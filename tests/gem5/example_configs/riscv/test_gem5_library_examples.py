# Copyright (c) 2021-2025 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from testlib import (
    config,
    gem5_verify_config,
    joinpath,
)
from testlib.configuration import constants

gem5_verify_config(
    name="test-gem5-library-example-riscv-ubuntu-run",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "riscv-ubuntu-run.py",
    ),
    config_args=[],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.very_long_tag,
)

gem5_verify_config(
    name="test-gem5-library-example-riscvmatched-hello",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "riscvmatched-hello.py",
    ),
    config_args=[],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.long_tag,
)

gem5_verify_config(
    name="test-gem5-library-example-riscvmatched-fs",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "riscvmatched-fs.py",
    ),
    config_args=["--to-init"],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.long_tag,
)

gem5_verify_config(
    name="test-gem5-library-example-riscvmatched-microbenchmark-suite",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "riscvmatched-microbenchmark-suite.py",
    ),
    config_args=[],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.long_tag,
)
