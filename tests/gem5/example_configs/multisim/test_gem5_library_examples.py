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

"""
This runs simple tests to ensure the examples in `configs/example/gem5_library`
still function. They simply check the simulation completed.
"""

from testlib import (
    config,
    constants,
    gem5_verify_config,
    joinpath,
    verifier,
)

gem5_verify_config(
    name="test-gem5-library-example-multisim-fs-x86-npb",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "multisim",
        "multisim-fs-x86-npb.py",
    ),
    config_args=[],
    gem5_args=["-m", "gem5.utils.multisim"],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.long_tag,
)

gem5_verify_config(
    name="test-gem5-library-example-multisim-print-this",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "multisim",
        "multisim-print-this.py",
    ),
    config_args=[],
    gem5_args=["-m", "gem5.utils.multisim"],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.quick_tag,
)

gem5_verify_config(
    name="test-gem5-library-example-multisim-print-this-list",
    fixtures=(),
    verifiers=(
        verifier.MatchStdoutNoPerf(
            joinpath(
                config.base_dir,
                "tests/gem5/example_configs",
                "multisim/ref/simout_multisim_print_this_list.txt",
            )
        ),
    ),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "multisim",
        "multisim-print-this.py",
    ),
    config_args=["--list"],
    gem5_args=[],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.quick_tag,
)

gem5_verify_config(
    name="test-gem5-library-example-multisim-print-this-single-process",
    fixtures=(),
    verifiers=(),
    config=joinpath(
        config.base_dir,
        "configs",
        "example",
        "gem5_library",
        "multisim",
        "multisim-print-this.py",
    ),
    config_args=["process_1"],
    gem5_args=[],
    valid_isas=(constants.all_compiled_tag,),
    valid_hosts=constants.supported_hosts,
    length=constants.quick_tag,
)
