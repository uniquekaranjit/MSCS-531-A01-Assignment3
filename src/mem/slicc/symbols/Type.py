# Copyright (c) 2020-2021 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 1999-2008 Mark D. Hill and David A. Wood
# Copyright (c) 2009 The Hewlett-Packard Development Company
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

from collections import OrderedDict

from slicc.symbols.Symbol import Symbol
from slicc.symbols.Var import Var
from slicc.util import PairContainer


class DataMember(Var):
    def __init__(
        self, symtab, ident, location, type, code, pairs, machine, init_code
    ):
        super().__init__(symtab, ident, location, type, code, pairs, machine)
        self.init_code = init_code
        self.real_c_type = self.type.c_ident
        if "template" in pairs:
            self.real_c_type += pairs["template"]


class Enumeration(PairContainer):
    def __init__(self, ident, pairs):
        super().__init__(pairs)
        self.ident = ident
        self.primary = False


class Type(Symbol):
    def __init__(
        self, table, ident, location, pairs, shared=False, machine=None
    ):
        super().__init__(table, ident, location, pairs)
        self.c_ident = ident
        self.abstract_ident = ""
        self.shared = shared
        if machine:
            if self.isExternal or self.isPrimitive:
                if "external_name" in self:
                    self.c_ident = self["external_name"]
            else:
                # Append with machine name
                self.c_ident = f"{machine}_{ident}"
        if shared or not table.slicc.protocol or self.isExternal:
            self.protocol_specific = ""
            self.gen_filename = self.c_ident
            self.header_string = self.c_ident
        else:
            self.protocol_specific = table.slicc.protocol
            self.gen_filename = self.protocol_specific + "/" + self.c_ident
            self.header_string = self.protocol_specific + "_" + self.c_ident

        self.pairs.setdefault("desc", "No description avaliable")

        # check for interface that this Type implements
        if "interface" in self:
            interface = self["interface"]
            if interface in ("Message"):
                self["message"] = "yes"

        # FIXME - all of the following id comparisons are fragile hacks
        if self.ident in ("CacheMemory"):
            self["cache"] = "yes"

        if self.ident in ("TBETable"):
            self["tbe"] = "yes"

        if self.ident == "TimerTable":
            self["timer"] = "yes"

        if self.ident == "DirectoryMemory":
            self["dir"] = "yes"

        if self.ident == "PersistentTable":
            self["persistent"] = "yes"

        if self.ident == "Prefetcher":
            self["prefetcher"] = "yes"

        self.isMachineType = ident == "MachineType"

        self.isStateDecl = "state_decl" in self
        self.statePermPairs = []

        self.data_members = OrderedDict()
        self.methods = {}
        self.enums = OrderedDict()

    @property
    def isPrimitive(self):
        return "primitive" in self

    @property
    def isMessage(self):
        return "message" in self

    @property
    def isTBE(self):
        return "tbe" in self

    @property
    def isBuffer(self):
        return "buffer" in self

    @property
    def isInPort(self):
        return "inport" in self

    @property
    def isOutPort(self):
        return "outport" in self

    @property
    def isEnumeration(self):
        return "enumeration" in self

    @property
    def isExternal(self):
        return "external" in self

    @property
    def isGlobal(self):
        return "global" in self

    @property
    def isInterface(self):
        return "interface" in self

    # Return false on error
    def addDataMember(self, ident, type, pairs, init_code):
        if ident in self.data_members:
            return False

        member = DataMember(
            self.symtab,
            ident,
            self.location,
            type,
            f"m_{ident}",
            pairs,
            None,
            init_code,
        )

        self.data_members[ident] = member
        self.symtab.registerSym(ident, member)
        return True

    def dataMemberType(self, ident):
        return self.data_members[ident].type

    def methodId(self, name, param_type_vec):
        return "_".join([name] + [pt.c_ident for pt in param_type_vec])

    def methodIdAbstract(self, name, param_type_vec):
        return "_".join([name] + [pt.abstract_ident for pt in param_type_vec])

    def statePermPairAdd(self, state_name, perm_name):
        self.statePermPairs.append([state_name, perm_name])

    def addFunc(self, func):
        ident = self.methodId(func.ident, func.param_types)
        if ident in self.methods:
            return False

        self.methods[ident] = func
        return True

    def addEnum(self, ident, pairs):
        if ident in self.enums:
            return False

        self.enums[ident] = Enumeration(ident, pairs)

        # Add default
        if "default" not in self:
            self["default"] = f"{self.c_ident}_NUM"

        return True

    ## Used to check if an enum has been already used and therefore
    ## should not be used again.
    def checkEnum(self, ident):
        if ident in self.enums and not self.enums[ident].primary:
            self.enums[ident].primary = True
            return True
        return False

    def writeCodeFiles(self, path, includes):
        if self.isExternal:
            # Do nothing
            pass
        elif self.isEnumeration:
            self.printEnumHH(path)
            self.printEnumCC(path)
        else:
            # User defined structs and messages
            self.printTypeHH(path)
            self.printTypeCC(path)

    def printTypeHH(self, path):
        code = self.symtab.codeFormatter()
        code(
            """
#ifndef __${{self.header_string}}_HH__
#define __${{self.header_string}}_HH__

#include <iostream>

#include "mem/ruby/slicc_interface/RubySlicc_Util.hh"

"""
        )

        for dm in self.data_members.values():
            if not dm.type.isPrimitive:
                code(
                    '#include "mem/ruby/protocol/$0.hh"', dm.type.gen_filename
                )

        parent = ""
        if "interface" in self:
            code('#include "mem/ruby/protocol/$0.hh"', self["interface"])
            parent = f" :  public {self['interface']}"

        code(
            """
namespace gem5
{

namespace ruby
{

class RubySystem;

"""
        )
        # For protocol-specific types, wrap in the protocol namespace
        if not self.shared:
            code(
                """
namespace ${{protocol}}
{
"""
            )

        code(
            """

$klass ${{self.c_ident}}$parent
{
  public:
""",
            klass="class",
        )

        if self.isMessage:
            code(
                "${{self.c_ident}}(Tick curTime, int blockSize, RubySystem* rs) : %s(curTime, blockSize, rs)"
                % self["interface"]
            )

            for dm in self.data_members.values():
                if dm.real_c_type in ("DataBlock", "WriteMask"):
                    code(f"\t\t, m_{dm.ident}(blockSize)")

            code("{")
            code("        setRubySystem(rs);")
            code("        block_size_bits = floorLog2(blockSize);")
        elif self.isTBE:
            code("${{self.c_ident}}(int block_size)")

            ctor_count = 0
            for dm in self.data_members.values():
                if dm.real_c_type in ("DataBlock", "WriteMask"):
                    if ctor_count == 0:
                        code("\t:")
                    else:
                        code("\t, ")
                    code(f"\t\tm_{dm.ident}(block_size)")
                    ctor_count += 1

            code("{")
            code("        block_size_bits = floorLog2(block_size);")
        else:
            code("${{self.c_ident}}()")

            ctor_count = 0
            for dm in self.data_members.values():
                if dm.real_c_type in ("DataBlock", "WriteMask"):
                    if ctor_count == 0:
                        code("\t:")
                    else:
                        code("\t, ")
                    code(f"\t\tm_{dm.ident}(0)")
                    ctor_count += 1

            code("{")

        code.indent()
        if not self.isGlobal:
            code.indent()
            for dm in self.data_members.values():
                ident = dm.ident
                if "default" in dm:
                    # look for default value
                    code(
                        'm_$ident = ${{dm["default"]}}; // default for this field'
                    )
                elif "default" in dm.type:
                    # Look for the type default
                    tid = dm.real_c_type
                    code('m_$ident = ${{dm.type["default"]}};')
                    code(" // default value of $tid")
                else:
                    code("// m_$ident has no default")

                # These parts of Messages need RubySystem pointers. For things
                # like Entry which only store NetDest, RubySystem is not needed.
                if self.isMessage and dm.real_c_type == "NetDest":
                    code("// m_$ident requires RubySystem")
                    code("m_$ident.setRubySystem(rs);")
            code.dedent()
        code("}")

        # ******** Copy constructor ********
        code("${{self.c_ident}}(const ${{self.c_ident}}&) = default;")

        # ******** Assignment operator ********

        code("${{self.c_ident}}")
        code("&operator=(const ${{self.c_ident}}&) = default;")

        # ******** Full init constructor ********
        if not self.isGlobal:
            params = [
                f"const {dm.real_c_type}& local_{dm.ident}"
                for dm in self.data_members.values()
            ]
            params = ", ".join(params)

            if self.isMessage:
                params = (
                    "const Tick curTime, const int blockSize, const RubySystem *rs, "
                    + params
                )

            code("${{self.c_ident}}($params)")

            # Call superclass constructor
            if "interface" in self:
                if self.isMessage:
                    code(
                        '    : ${{self["interface"]}}(curTime, blockSize, rs)'
                    )

                    for dm in self.data_members.values():
                        if dm.real_c_type in ("DataBlock", "WriteMask"):
                            code(f"\t\t, m_{dm.ident}(blockSize)")
                else:
                    code('    : ${{self["interface"]}}()')

                    for dm in self.data_members.values():
                        if dm.real_c_type in ("DataBlock", "WriteMask"):
                            code(f"\t\t, m_{dm.ident}(local_{dm.ident})")
            else:
                ctor_count = 0
                for dm in self.data_members.values():
                    if dm.real_c_type in ("DataBlock", "WriteMask"):
                        if ctor_count == 0:
                            code("\t:")
                        else:
                            code("\t, ")
                        code(f"\t\tm_{dm.ident}(local_{dm.ident})")
                        ctor_count += 1

            code("{")
            code.indent()
            for dm in self.data_members.values():
                if not dm.real_c_type in ("DataBlock", "WriteMask"):
                    code("m_${{dm.ident}} = local_${{dm.ident}};")

            code.dedent()
            code("}")

        # create a clone member
        if self.isMessage:
            code(
                """
MsgPtr
clone() const
{
     return std::shared_ptr<Message>(new ${{self.c_ident}}(*this));
}
"""
            )
        else:
            code(
                """
${{self.c_ident}}*
clone() const
{
     return new ${{self.c_ident}}(*this);
}
"""
            )

        if not self.isGlobal:
            # Block size setter for fields that require block size
            # Intentionally do not begin function name with "set" in case
            # the user has a field named BlockSize which would conflict
            # with the method generated below.
            code("\nvoid initBlockSize(int block_size)")
            code("{")
            code("\tblock_size_bits = floorLog2(block_size);")

            needs_block_size = (
                "DataBlock",
                "WriteMask",
                "PersistentTable",
                "TimerTable",
                "PerfectCacheMemory",
            )

            for dm in self.data_members.values():
                if dm.real_c_type in needs_block_size:
                    code(f"\tm_{dm.ident}.setBlockSize(block_size);")
            code("}\n")

            code("\nvoid setRubySystem(RubySystem *ruby_system)")
            code("{")
            for dm in self.data_members.values():
                if dm.real_c_type in ("NetDest"):
                    code(f"// m_{dm.ident} requires RubySystem")
                    code(f"\tm_{dm.ident}.setRubySystem(ruby_system);")
            code("}\n")

            # const Get methods for each field
            code("// Const accessors methods for each field")
            for dm in self.data_members.values():
                code(
                    """
/** \\brief Const accessor method for ${{dm.ident}} field.
 *  \\return ${{dm.ident}} field
 */
const ${{dm.real_c_type}}&
get${{dm.ident}}() const
{
    return m_${{dm.ident}};
}
"""
                )

            # Non-const Get methods for each field
            code("// Non const Accessors methods for each field")
            for dm in self.data_members.values():
                code(
                    """
/** \\brief Non-const accessor method for ${{dm.ident}} field.
 *  \\return ${{dm.ident}} field
 */
${{dm.real_c_type}}&
get${{dm.ident}}()
{
    return m_${{dm.ident}};
}
"""
                )

            # Set methods for each field
            code("// Mutator methods for each field")
            for dm in self.data_members.values():
                code(
                    """
/** \\brief Mutator method for ${{dm.ident}} field */
void
set${{dm.ident}}(const ${{dm.real_c_type}}& local_${{dm.ident}})
{
    m_${{dm.ident}} = local_${{dm.ident}};
}
"""
                )

        code("void print(std::ostream& out) const;")
        code.dedent()
        code("  //private:")
        code.indent()

        # block_size_bits for print methods
        code("int block_size_bits = 0;")

        # Data members for each field
        for dm in self.data_members.values():
            if "abstract" not in dm:
                const = ""
                init = ""

                # global structure
                if self.isGlobal:
                    const = "static const "

                # init value
                if dm.init_code:
                    # only global structure can have init value here
                    assert self.isGlobal
                    init = f" = {dm.init_code}"

                if "desc" in dm:
                    code('/** ${{dm["desc"]}} */')

                code("$const${{dm.real_c_type}} m_${{dm.ident}}$init;")

        # Prototypes for methods defined for the Type
        for item in self.methods:
            proto = self.methods[item].prototype
            if proto:
                code("$proto")

        code.dedent()
        code("};")

        code(
            """
inline ::std::ostream&
operator<<(::std::ostream& out, const ${{self.c_ident}}& obj)
{
    obj.print(out);
    out << ::std::flush;
    return out;
}

"""
        )
        # For protocol-specific types, close the protocol namespace
        if not self.shared:
            code(
                """
} // namespace ${{protocol}}
"""
            )

        code(
            """
} // namespace ruby
} // namespace gem5

#endif // __${{self.header_string}}_HH__
"""
        )

        code.write(path, f"{self.gen_filename}.hh")

    def printTypeCC(self, path):
        code = self.symtab.codeFormatter()

        code(
            """
#include <iostream>
#include <memory>

#include "mem/ruby/protocol/${{self.gen_filename}}.hh"
#include "mem/ruby/system/RubySystem.hh"

namespace gem5
{

namespace ruby
{
"""
        )
        # For protocol-specific types, wrap in the protocol namespace
        if not self.shared:
            code(
                """

namespace ${{protocol}}
{
"""
            )

        code(
            """

/** \\brief Print the state of this object */
void
${{self.c_ident}}::print(std::ostream& out) const
{
    out << "[${{self.c_ident}}: ";
"""
        )

        # For each field
        code.indent()
        for dm in self.data_members.values():
            if dm.type.c_ident == "Addr":
                code(
                    """
out << "${{dm.ident}} = " << printAddress(m_${{dm.ident}}, block_size_bits) << " ";"""
                )
            else:
                code('out << "${{dm.ident}} = " << m_${{dm.ident}} << " ";' "")

        code.dedent()

        # Trailer
        code(
            """
    out << "]";
}"""
        )

        # print the code for the methods in the type
        for item in self.methods:
            code(self.methods[item].generateCode())

        # For protocol-specific types, close the protocol namespace
        if not self.shared:
            code(
                """

} // namespace ${{protocol}}
"""
            )

        code(
            """
} // namespace ruby
} // namespace gem5
"""
        )

        code.write(path, f"{self.gen_filename}.cc")

    def printEnumHH(self, path):
        code = self.symtab.codeFormatter()
        code(
            """
#ifndef __${{self.header_string}}_HH__
#define __${{self.header_string}}_HH__

#include <iostream>
#include <string>

"""
        )
        if self.isStateDecl:
            code('#include "mem/ruby/protocol/AccessPermission.hh"')

        if self.isMachineType:
            code("#include <functional>")
            code('#include "base/logging.hh"')
            code('#include "mem/ruby/common/Address.hh"')
            code('#include "mem/ruby/common/TypeDefines.hh"')

        code(
            """
namespace gem5
{

namespace ruby
{

"""
        )
        # For protocol-specific types, wrap in the protocol namespace
        if not self.shared:
            code(
                """

namespace ${{protocol}}
{
"""
            )

        if self.isMachineType:
            code("struct MachineID;")

        code(
            """

// Class definition
/** \\enum ${{self.c_ident}}
 *  \\brief ${{self.desc}}
 */
enum ${{self.c_ident}} {
    ${{self.c_ident}}_FIRST,
"""
        )

        code.indent()
        # For each field
        for i, (ident, enum) in enumerate(self.enums.items()):
            desc = enum.get("desc", "No description avaliable")
            if i == 0:
                init = f" = {self.c_ident}_FIRST"
            else:
                init = ""
            code("${{self.c_ident}}_${{enum.ident}}$init, /**< $desc */")
        code.dedent()
        code(
            """
    ${{self.c_ident}}_NUM
};

// Code to convert from a string to the enumeration
${{self.c_ident}} string_to_${{self.c_ident}}(const ::std::string& str);

// Code to convert state to a string
::std::string ${{self.c_ident}}_to_string(const ${{self.c_ident}}& obj);

// Code to increment an enumeration type
${{self.c_ident}} &operator++(${{self.c_ident}} &e);
"""
        )

        # MachineType hack used to set the base component id for each Machine
        if self.isMachineType:
            code(
                """
int ${{self.c_ident}}_base_level(const ${{self.c_ident}}& obj);
MachineType ${{self.c_ident}}_from_base_level(int);
int ${{self.c_ident}}_base_number(const ${{self.c_ident}}& obj);
int ${{self.c_ident}}_base_count(const ${{self.c_ident}}& obj);
"""
            )

            for enum in self.enums.values():
                code(
                    """

MachineID get${{enum.ident}}MachineID(NodeID RubyNode);
"""
                )

        if self.isStateDecl:
            code(
                """

// Code to convert the current state to an access permission
AccessPermission ${{self.c_ident}}_to_permission(const ${{self.c_ident}}& obj);

"""
            )

        code(
            """

::std::ostream&
operator<<(::std::ostream& out, const ${{self.c_ident}}& obj);

"""
        )

        # For protocol-specific types, close the protocol namespace
        if not self.shared:
            code(
                """
} // namespace ${{protocol}}
"""
            )

        code(
            """
} // namespace ruby
} // namespace gem5
"""
        )

        if self.isMachineType:
            code(
                """

// define a hash function for the MachineType class
namespace std {
template<>
struct hash<gem5::ruby::MachineType>
{
    std::size_t
    operator()(const gem5::ruby::MachineType &mtype) const
    {
        return hash<size_t>()(static_cast<size_t>(mtype));
    }
};
}

"""
            )

        # Trailer
        code(
            """
#endif // __${{self.header_string}}_HH__
"""
        )

        code.write(path, f"{self.gen_filename}.hh")

    def printEnumCC(self, path):
        code = self.symtab.codeFormatter()
        code(
            """
#include <cassert>
#include <iostream>
#include <string>

#include "base/logging.hh"
#include "mem/ruby/protocol/${{self.gen_filename}}.hh"

"""
        )

        if self.isStateDecl:
            code(
                """
namespace gem5
{

namespace ruby
{
"""
            )
            # For protocol-specific types, wrap in the protocol namespace
            if not self.shared:
                code(
                    """

namespace ${{protocol}}
{
"""
                )

            code(
                """

// Code to convert the current state to an access permission
AccessPermission ${{self.c_ident}}_to_permission(const ${{self.c_ident}}& obj)
{
    switch(obj) {
"""
            )
            # For each case
            code.indent()
            for statePerm in self.statePermPairs:
                code("  case ${{self.c_ident}}_${{statePerm[0]}}:")
                code("    return AccessPermission_${{statePerm[1]}};")
            code.dedent()
            code(
                """
      default:
        panic("Unknown state access permission converstion for ${{self.c_ident}}");
    }
    // Appease the compiler since this function has a return value
    return AccessPermission_Invalid;
}

"""
            )

            # For protocol-specific types, close the protocol namespace
            if not self.shared:
                code(
                    """
} // namespace ${{protocol}}
"""
                )

            code(
                """

} // namespace ruby
} // namespace gem5

"""
            )

        if self.isMachineType:
            code('#include "mem/ruby/common/MachineID.hh"')
            code('#include "mem/ruby/system/RubySystem.hh"')

        code(
            """
namespace gem5
{

namespace ruby
{
"""
        )
        # For protocol-specific types, wrap in the protocol namespace
        if not self.shared:
            code(
                """

namespace ${{protocol}}
{
"""
            )
        code(
            """

// Code for output operator
::std::ostream&
operator<<(::std::ostream& out, const ${{self.c_ident}}& obj)
{
    out << ${{self.c_ident}}_to_string(obj);
    out << ::std::flush;
    return out;
}

// Code to convert state to a string
std::string
${{self.c_ident}}_to_string(const ${{self.c_ident}}& obj)
{
    switch(obj) {
"""
        )

        # For each field
        code.indent()
        for enum in self.enums.values():
            code("  case ${{self.c_ident}}_${{enum.ident}}:")
            code('    return "${{enum.ident}}";')
        code("  case ${{self.c_ident}}_NUM:")
        code('    return "NUM (invalid)";')
        code.dedent()

        # Trailer
        code(
            """
      default:
        panic("Invalid value for type ${{self.c_ident}} %d\\n", obj);
    }
    // Appease the compiler since this function has a return value
    return "";
}

// Code to convert from a string to the enumeration
${{self.c_ident}}
string_to_${{self.c_ident}}(const std::string& str)
{
"""
        )

        # For each field
        start = ""
        code.indent()
        for enum in self.enums.values():
            code('${start}if (str == "${{enum.ident}}") {')
            code("    return ${{self.c_ident}}_${{enum.ident}};")
            start = "} else "
        code.dedent()

        code(
            """
    } else {
        panic("Invalid string conversion for %s, type ${{self.c_ident}}", str);
    }
}

// Code to increment an enumeration type
${{self.c_ident}}&
operator++(${{self.c_ident}}& e)
{
    assert(e < ${{self.c_ident}}_NUM);
    return e = ${{self.c_ident}}(e+1);
}
"""
        )

        # MachineType hack used to set the base level and number of
        # components for each Machine
        if self.isMachineType:
            code(
                """
/** \\brief returns the base vector index for each machine type to be
  * used by NetDest
  *
  * \\return the base vector index for each machine type to be used by NetDest
  * \\see NetDest.hh
  */
int
${{self.c_ident}}_base_level(const ${{self.c_ident}}& obj)
{
    switch(obj) {
"""
            )

            # For each field
            code.indent()
            for i, enum in enumerate(self.enums.values()):
                code("  case ${{self.c_ident}}_${{enum.ident}}:")
                code("    return $i;")
            code.dedent()

            # total num
            code(
                """
      case ${{self.c_ident}}_NUM:
        return ${{len(self.enums)}};

      default:
        panic("Invalid value for type ${{self.c_ident}} %d\\n", obj);
    }
    // Appease the compiler since this function has a return value
    return -1;
}

/** \\brief returns the machine type for each base vector index used by NetDest
 *
 * \\return the MachineType
 */
MachineType
${{self.c_ident}}_from_base_level(int type)
{
    switch(type) {
"""
            )

            # For each field
            code.indent()
            for i, enum in enumerate(self.enums.values()):
                code("  case $i:")
                code("    return ${{self.c_ident}}_${{enum.ident}};")
            code.dedent()

            # Trailer
            code(
                """
      default:
        panic("Invalid value for type ${{self.c_ident}} %d\\n", type);
    }
}

/** \\brief The return value indicates the number of components created
 * before a particular machine\'s components
 *
 * \\return the base number of components for each machine
 */
int
RubySystem::${{self.c_ident}}_base_number(const ${{self.c_ident}}& obj)
{
    int base = 0;
    switch(obj) {
"""
            )

            # For each field
            code.indent()
            code("  case ${{self.c_ident}}_NUM:")
            for enum in reversed(list(self.enums.values())):
                code(
                    "    base += m_num_controllers[${{self.c_ident}}_${{enum.ident}}];"
                )
                code("    [[fallthrough]];")
                code("  case ${{self.c_ident}}_${{enum.ident}}:")
            code("    break;")
            code.dedent()

            code(
                """
      default:
        panic("Invalid value for type ${{self.c_ident}} %d\\n", obj);
    }

    return base;
}

/** \\brief returns the total number of components for each machine
 * \\return the total number of components for each machine
 */
int
RubySystem::${{self.c_ident}}_base_count(const ${{self.c_ident}}& obj)
{
    switch(obj) {
"""
            )

            # For each field
            for enum in self.enums.values():
                code("case ${{self.c_ident}}_${{enum.ident}}:")
                code(
                    "return m_num_controllers[${{self.c_ident}}_${{enum.ident}}];"
                )

            # total num
            code(
                """
      case ${{self.c_ident}}_NUM:
      default:
        panic("Invalid value for type ${{self.c_ident}} %d\\n", obj);
    }
    // Appease the compiler since this function has a return value
    return -1;
}
"""
            )

            for enum in self.enums.values():
                code(
                    """

MachineID
get${{enum.ident}}MachineID(NodeID RubyNode)
{
      MachineID mach = {MachineType_${{enum.ident}}, RubyNode};
      return mach;
}
"""
                )

        # For protocol-specific types, close the protocol namespace
        if not self.shared:
            code(
                """

} // namespace ${{protocol}}
"""
            )

        code(
            """
} // namespace ruby
} // namespace gem5
"""
        )

        # Write the file
        code.write(path, f"{self.gen_filename}.cc")


__all__ = ["Type"]
