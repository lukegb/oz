import oz.TDL
import oz.GuestFactory
import ConfigParser
import StringIO
import logging
import os
import sys

success = 0
fail = 0

def default_route():
    route_file = "/proc/net/route"
    d = file(route_file)

    defn = 0
    for line in d.xreadlines():
        info = line.split()
        if (len(info) != 11): # 11 = typical num of fields in the file
            logging.warn(_("Invalid line length while parsing %s.") %
                         (route_file))
            break
        try:
            route = int(info[1], 16)
            if route == 0:
                return info[0]
        except ValueError:
            continue
    raise Exception, "Could not find default route"

def test_distro(distro, version, arch, installtype):
    tdlxml = """
<template>
  <name>tester</name>
  <os>
    <name>%s</name>
    <version>%s</version>
    <arch>%s</arch>
    <install type='%s'>
      <%s>http://example.org</%s>
    </install>
    <key></key>
  </os>
</template>
""" % (distro, version, arch, installtype, installtype, installtype)

    tdl = oz.TDL.TDL(tdlxml)

    # we find the default route for this machine.  Note that this very well
    # may not be a bridge, but for the purposes of testing the factory, it
    # doesn't really matter; it just has to have an IP address
    route = default_route()

    config = ConfigParser.SafeConfigParser()
    config.readfp(StringIO.StringIO("[libvirt]\nuri=qemu:///session\nbridge_name=%s" % route))

    if os.getenv('DEBUG') != None:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    guest = oz.GuestFactory.guest_factory(tdl, config, None)

def runtest(distro, version, arch, installtype, expect_success):
    global success
    global fail

    print "Testing %s-%s-%s-%s..." % (distro, version, arch, installtype),
    try:
        test_distro(distro, version, arch, installtype)
        if expect_success:
            success += 1
            print "OK"
        else:
            fail += 1
            print "FAIL"
    except Exception, e:
        if expect_success:
            fail += 1
            print e
            print "FAIL"
        else:
            success += 1
            print "OK"

def expect_success(distro, version, arch, installtype):
    return runtest(distro, version, arch, installtype, True)

def expect_fail(distro, version, arch, installtype):
    return runtest(distro, version, arch, installtype, False)

# bad distro
expect_fail("foo", "1", "i386", "url")
# bad installtype
expect_fail("Fedora", "14", "i386", "dong")
# bad arch
expect_fail("Fedora", "14", "ia64", "iso")

# FedoraCore
for version in ["1", "2", "3", "4", "5", "6"]:
    for arch in ["i386", "x86_64"]:
        for installtype in ["url", "iso"]:
            expect_success("FedoraCore", version, arch, installtype)
# bad FedoraCore version
expect_fail("FedoraCore", "24", "x86_64", "iso")

# Fedora
for version in ["7", "8", "9", "10", "11", "12", "13", "14", "15"]:
    for arch in ["i386", "x86_64"]:
        for installtype in ["url", "iso"]:
            expect_success("Fedora", version, arch, installtype)
# bad Fedora version
expect_fail("Fedora", "24", "x86_64", "iso")

# RHL
for version in ["7.0", "7.1", "7.2", "7.3", "8", "9"]:
    expect_success("RHL", version, "i386", "url")
# bad RHL version
expect_fail("RHL", "10", "i386", "url")
# bad RHL arch
expect_fail("RHL", "9", "x86_64", "url")
# bad RHL installtype
expect_fail("RHL", "9", "x86_64", "iso")

# RHEL-2.1
for version in ["GOLD", "U2", "U3", "U4", "U5", "U6"]:
    expect_success("RHEL-2.1", version, "i386", "url")
# bad RHEL-2.1 version
expect_fail("RHEL-2.1", "U7", "i386", "url")
# bad RHEL-2.1 arch
expect_fail("RHEL-2.1", "U6", "x86_64", "url")
# bad RHEL-2.1 installtype
expect_fail("RHEL-2.1", "U6", "i386", "iso")

# RHEL-3
for version in ["GOLD", "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9"]:
    for arch in ["i386", "x86_64"]:
        expect_success("RHEL-3", version, arch, "url")
# bad RHEL-3 version
expect_fail("RHEL-3", "U10", "x86_64", "url")
# invalid RHEL-3 installtype
expect_fail("RHEL-3", "U9", "x86_64", "iso")

# RHEL-4/CentOS-4
for distro in ["RHEL-4", "CentOS-4"]:
    for version in ["GOLD", "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9"]:
        for arch in ["i386", "x86_64"]:
            for installtype in ["url", "iso"]:
                expect_success(distro, version, arch, installtype)
# bad RHEL-4 version
expect_fail("RHEL-4", "U10", "x86_64", "url")

# RHEL-5/CentOS-5
for distro in ["RHEL-5", "CentOS-5"]:
    for version in ["GOLD", "U1", "U2", "U3", "U4", "U5", "U6"]:
        for arch in ["i386", "x86_64"]:
            for installtype in ["url", "iso"]:
                expect_success(distro, version, arch, installtype)
# bad RHEL-5 version
expect_fail("RHEL-5", "U10", "x86_64", "url")

# RHEL-6
for version in ["0", "1"]:
    for arch in ["i386", "x86_64"]:
        for installtype in ["url", "iso"]:
            expect_success("RHEL-6", version, arch, installtype)
# bad RHEL-6 version
expect_fail("RHEL-6", "U10", "x86_64", "url")

# Debian
for version in ["5", "6"]:
    for arch in ["i386", "x86_64"]:
        expect_success("Debian", version, arch, "iso")
# bad Debian version
expect_fail("Debian", "12", "i386", "iso")
# invalid Debian installtype
expect_fail("Debian", "6", "x86_64", "url")

# Windows
expect_success("Windows", "2000", "i386", "iso")
for version in ["XP", "2003", "2008", "7"]:
    for arch in ["i386", "x86_64"]:
        expect_success("Windows", version, arch, "iso")
# bad Windows 2000 arch
expect_fail("Windows", "2000", "x86_64", "iso")
# bad Windows version
expect_fail("Windows", "1999", "x86_64", "iso")
# invalid Windows installtype
expect_fail("Windows", "2008", "x86_64", "url")

# OpenSUSE
for version in ["11.0", "11.1", "11.2", "11.3", "11.4"]:
    for arch in ["i386", "x86_64"]:
        expect_success("OpenSUSE", version, arch, "iso")
# bad OpenSUSE version
expect_fail("OpenSUSE", "16", "x86_64", "iso")
# invalid OpenSUSE installtype
expect_fail("OpenSUSE", "11.4", "x86_64", "url")

# Ubuntu
for version in ["6.06", "6.06.1", "6.06.2", "6.10", "7.04", "7.10", "8.04",
                "8.04.1", "8.04.2", "8.04.3", "8.04.4", "8.10", "9.04", "9.10",
                "10.04", "10.04.1", "10.10", "11.04"]:
    for arch in ["i386", "x86_64"]:
        expect_success("Ubuntu", version, arch, "iso")
# bad Ubuntu version
expect_fail("Ubuntu", "10.9", "i386", "iso")
# bad Ubuntu installtype
expect_fail("Ubuntu", "10.10", "i386", "url")

print "SUCCESS: %d, FAIL: %d" % (success, fail)

sys.exit(fail)
