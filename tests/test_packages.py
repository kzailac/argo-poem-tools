import subprocess
import unittest
from unittest import mock

from argo_poem_tools.packages import Packages, _compare_versions, _compare_vr, \
    PackageException

data = {
    "argo-devel": {
        "content": "[argo-devel]\n"
                   "name=ARGO Product Repository\n"
                   "baseurl=http://rpm-repo.argo.grnet.gr/ARGO/"
                   "devel/centos6/\n"
                   "gpgcheck=0\n"
                   "enabled=1\n"
                   "priority=99\n"
                   "exclude=\n"
                   "includepkgs=\n",
        "packages": [
            {
                "name": "nagios-plugins-fedcloud",
                "version": "0.5.0"
            },
            {
                "name": "nagios-plugins-igtf",
                "version": "1.4.0"
            },
            {
                "name": "nagios-plugins-globus",
                "version": "0.1.5"
            },
            {
                "name": "nagios-plugins-argo",
                "version": "0.1.12"
            }
        ]
    },
    "epel": {
        "content": "[epel]\n"
                   "name=Extra Packages for Enterprise Linux 7 - $basearch\n"
                   "mirrorlist=https://mirrors.fedoraproject.org/metalink?"
                   "repo=epel-7&arch=$basearch\n"
                   "failovermethod=priority\n"
                   "enabled=1\n"
                   "gpgcheck=1\n"
                   "gpgkey=https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-"
                   "EPEL-7",
        "packages": [
            {
                "name": "nagios-plugins-http",
                "version": "present"
            }
        ]
    }
}

mock_yum_list_available = \
"""
Loaded plugins: fastestmirror, ovl
Loading mirror speeds from cached hostfile
 * base: mirror.centos.plus.hr
 * epel: centos.anexia.at
 * extras: mirror.centos.plus.hr
 * updates: mirror.centos.plus.hr
Available Packages
nagios.x86_64                             4.4.5-7.el7                    epel   
nagios-contrib.x86_64                     4.4.5-7.el7                    epel   
nagios-devel.x86_64                       4.4.5-7.el7                    epel   
nagios-plugin-grnet-agora.noarch          0.3-20200731072952.4427855.el7 argo-devel
nagios-plugins-activemq.noarch            1.0.0-20170401112243.00c5f1d.el7 argo-devel
nagios-plugins-disk_smb.x86_64            2.3.3-2.el7                    epel   
nagios-plugins-globus.noarch              0.1.5-20200713050450.eb1e7d8.el7 argo-devel  
nagios-plugins-gocdb.noarch               1.0.0-20200713050609.a481696.el7 argo-devel  
NetworkManager-dispatcher-routing-rules.noarch
                                          1:1.18.4-3.el7                 base

""".encode('utf-8')

mock_rpm_qa = \
"""
nagios-plugins-2.3.3-2.el7.x86_64
nagios-plugins-file_age-2.3.3-2.el7.x86_64
nagios-plugins-argo-0.1.13-20200901060701.5869b94.el7.noarch
nagios-plugins-fedcloud-0.5.2-20200511071632.05e2501.el7.noarch
nagios-plugins-igtf-1.4.0-20200713050846.f6ca58d.el7.noarch
nagios-plugins-dummy-2.3.3-2.el7.x86_64
nagios-common-4.4.5-7.el7.x86_64
nagios-plugins-perl-2.3.3-2.el7.x86_64
nagios-plugins-http-2.3.3-2.el7.x86_64

""".encode('utf-8')

mock_yum_versionlock_list = \
"""
Loaded plugins: fastestmirror, ovl, versionlock
0:nagios-plugins-argo-0.1.12-20200811040245.d758e91.el7.*
0:nagios-plugins-fedcloud-0.5.2-20201217023205.1b502c8.el7.*
versionlock list done
""".encode('utf-8')

mock_empty_versionlock_list = \
"""
Loaded plugins: fastestmirror, ovl, versionlock
versionlock list done
""".encode('utf-8')


def mock_func(*args, **kwargs):
    pass


def mock_func_exception(*args, **kwargs):
    if args and args[0] == ['yum', 'versionlock', 'add', 'nagios-plugins-igtf']:
        raise subprocess.CalledProcessError(None, None)

    else:
        raise Exception('An error.')


class RPMTests(unittest.TestCase):
    def test_compare_versions(self):
        self.assertEqual(_compare_versions('1.0.0', '1.0.0'), 0)
        self.assertEqual(_compare_versions('2.0.0', '1.0.0'), 1)
        self.assertEqual(_compare_versions('1.1.0', '1.0.0'), 1)
        self.assertEqual(_compare_versions('1.0.1', '1.0.0'), 1)
        self.assertEqual(_compare_versions('1.1.1', '1.0.0'), 1)
        self.assertEqual(_compare_versions('1.0.0', '2.1.0'), -1)
        self.assertEqual(_compare_versions('1.0.0', '1.1.0'), -1)
        self.assertEqual(_compare_versions('1.0.0', '1.1.1'), -1)
        self.assertEqual(_compare_versions('1.0.0', '1.0.2'), -1)
        self.assertEqual(_compare_versions('0.1', '1.0'), -1)
        self.assertEqual(_compare_versions('0.2', '0.1'), 1)
        self.assertEqual(_compare_versions('2', '1'), 1)
        self.assertEqual(_compare_versions('1', '2'), -1)
        self.assertEqual(_compare_versions('0.1.9', '0.1.13'), -1)
        self.assertEqual(_compare_versions("1.0", "1.0.1"), -1)
        self.assertEqual(
            _compare_versions(
                '20200408044026.7943b04.el7',
                '20200408052214.4d1470e.el7'
            ), -1
        )

    def test_compare_vr(self):
        self.assertEqual(
            _compare_vr(
                ('0.5.2', '20200408044026.7943b04.el7'),
                ('0.5.2', '20200408052214.4d1470e.el7')
            ),
            -1
        )
        self.assertEqual(
            _compare_vr(
                ('0.5.3', '20200408044026.7943b04.el7'),
                ('0.5.2', '20200408052214.4d1470e.el7')
            ),
            1
        )
        self.assertEqual(
            _compare_vr(
                ('0.5.2', '20200408052214.4d1470e.el7'),
                ('0.5.2', '20200408052214.4d1470e.el7')
            ),
            0
        )
        self.assertEqual(_compare_vr(('1', '1.el7'), ('1', '2.el7')), -1)
        self.assertEqual(_compare_vr(('2', '1.el7'), ('1', '2.el7')), 1)
        self.assertEqual(
            _compare_vr(('0.0.1', '1.el7'), ('1.0.0', '2.el7')), -1
        )
        self.assertEqual(_compare_vr(('2.0.1', '1.el7'), ('1.0.0', '2.el7')), 1)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.pkgs = Packages(data)

    def test_get_package_list(self):
        self.assertEqual(
            set(self.pkgs.package_list),
            {
                ('nagios-plugins-fedcloud', '0.5.0'),
                ('nagios-plugins-igtf', '1.4.0'),
                ('nagios-plugins-globus', '0.1.5'),
                ('nagios-plugins-argo', '0.1.12'),
                ('nagios-plugins-http', )
            }
        )

    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_get_available_packages(self, mock_yumdb):
        self.pkgs.versions_unlocked = True
        mock_yumdb.return_value = mock_yum_list_available
        self.assertEqual(
            self.pkgs._get_available_packages(),
            [
                dict(name='nagios', version='4.4.5', release='7.el7'),
                dict(name='nagios-contrib', version='4.4.5', release='7.el7'),
                dict(name='nagios-devel', version='4.4.5', release='7.el7'),
                dict(name='nagios-plugin-grnet-agora', version='0.3',
                     release='20200731072952.4427855.el7'),
                dict(name='nagios-plugins-activemq', version='1.0.0',
                     release='20170401112243.00c5f1d.el7'),
                dict(name='nagios-plugins-disk_smb', version='2.3.3',
                     release='2.el7'),
                dict(name='nagios-plugins-globus', version='0.1.5',
                     release='20200713050450.eb1e7d8.el7'),
                dict(name='nagios-plugins-gocdb', version='1.0.0',
                     release='20200713050609.a481696.el7'),
                dict(name='NetworkManager-dispatcher-routing-rules',
                     version='1:1.18.4', release='3.el7')
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._unlock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_get_available_packages_if_versions_locked(
            self, mock_yumdb, mock_unlock
    ):
        mock_yumdb.return_value = mock_yum_list_available
        self.assertEqual(
            self.pkgs._get_available_packages(),
            [
                dict(name='nagios', version='4.4.5', release='7.el7'),
                dict(name='nagios-contrib', version='4.4.5', release='7.el7'),
                dict(name='nagios-devel', version='4.4.5', release='7.el7'),
                dict(name='nagios-plugin-grnet-agora', version='0.3',
                     release='20200731072952.4427855.el7'),
                dict(name='nagios-plugins-activemq', version='1.0.0',
                     release='20170401112243.00c5f1d.el7'),
                dict(name='nagios-plugins-disk_smb', version='2.3.3',
                     release='2.el7'),
                dict(name='nagios-plugins-globus', version='0.1.5',
                     release='20200713050450.eb1e7d8.el7'),
                dict(name='nagios-plugins-gocdb', version='1.0.0',
                     release='20200713050609.a481696.el7'),
                dict(name='NetworkManager-dispatcher-routing-rules',
                     version='1:1.18.4', release='3.el7')
            ]
        )
        self.assertEqual(mock_unlock.call_count, 1)

    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_get_locked_versions(self, mock_versionlock):
        mock_versionlock.return_value = mock_yum_versionlock_list
        self.pkgs._get_locked_versions()
        self.assertEqual(
            sorted(self.pkgs.locked_versions),
            ['nagios-plugins-argo', 'nagios-plugins-fedcloud']
        )

    @mock.patch('argo_poem_tools.packages.subprocess.call')
    def test_unlock_versions(self, mock_call):
        self.pkgs.locked_versions = [
            'nagios-plugins-argo', 'nagios-plugins-fedcloud'
        ]
        self.assertEqual(self.pkgs.initially_locked_versions, [])
        mock_call.side_effect = mock_func
        self.pkgs._unlock_versions()
        self.assertEqual(mock_call.call_count, 2)
        mock_call.assert_has_calls([
            mock.call(
                ['yum', 'versionlock', 'delete', 'nagios-plugins-argo'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ),
            mock.call(
                ['yum', 'versionlock', 'delete', 'nagios-plugins-fedcloud'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        ], any_order=True)
        self.assertEqual(
            self.pkgs.initially_locked_versions,
            ['nagios-plugins-argo', 'nagios-plugins-fedcloud']
        )

    @mock.patch('argo_poem_tools.packages.subprocess.call')
    def test_failsafe_lock_versions(self, mock_call):
        mock_call.side_effect = mock_func
        self.pkgs.initially_locked_versions = [
            'nagios-plugins-argo', 'nagios-plugins-fedcloud',
            'nagios-plugins-globus'
        ]
        self.pkgs.locked_versions = ['nagios-plugins-argo']
        self.pkgs._failsafe_lock_versions()
        self.assertEqual(mock_call.call_count, 3)
        mock_call.assert_has_calls(
            [
                mock.call(
                    ['yum', 'versionlock', 'add', 'nagios-plugins-argo'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                ),
                mock.call(
                    ['yum', 'versionlock', 'add', 'nagios-plugins-fedcloud'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                ),
                mock.call(
                    ['yum', 'versionlock', 'add', 'nagios-plugins-globus'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            ], any_order=True
        )

    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    @mock.patch('argo_poem_tools.packages.subprocess.call')
    def test_unlock_versions_if_none_locked(self, mock_call, mock_versionlock):
        mock_call.side_effect = mock_func
        mock_versionlock.return_value = mock_empty_versionlock_list
        self.assertEqual(self.pkgs.initially_locked_versions, [])
        self.pkgs._unlock_versions()
        self.assertEqual(mock_call.call_count, 0)
        self.assertEqual(self.pkgs.initially_locked_versions, [])

    @mock.patch('argo_poem_tools.packages.Packages._get_available_packages')
    def test_get_exceptions(self, mock_yumdb):
        mock_yumdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.6.0',
                 release='20200511071632.05e2501.el7'),
            dict(name='nagios-plugins-igtf', version='1.4.0', release='3.el7'),
            dict(name='nagios-plugins-http', version='2.3.3', release='1.el7')
        ]
        self.pkgs._get_exceptions()
        self.assertEqual(
            self.pkgs.packages_different_version,
            [('nagios-plugins-fedcloud', '0.6.0')]
        )
        self.assertEqual(
            set(self.pkgs.packages_not_found),
            {
                ('nagios-plugins-globus', '0.1.5'),
                ('nagios-plugins-argo', '0.1.12')
            }
        )

    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_get_installed_packages(self, mock_rpm):
        mock_rpm.return_value = mock_rpm_qa
        self.assertEqual(
            self.pkgs._get_installed_packages(),
            [
                dict(name='nagios-plugins', version='2.3.3', release='2.el7'),
                dict(name='nagios-plugins-file_age', version='2.3.3',
                     release='2.el7'),
                dict(name='nagios-plugins-argo', version='0.1.13',
                     release='20200901060701.5869b94.el7'),
                dict(name='nagios-plugins-fedcloud', version='0.5.2',
                     release='20200511071632.05e2501.el7'),
                dict(name='nagios-plugins-igtf', version='1.4.0',
                     release='20200713050846.f6ca58d.el7'),
                dict(name='nagios-plugins-dummy', version='2.3.3',
                     release='2.el7'),
                dict(name='nagios-common', version='4.4.5', release='7.el7'),
                dict(name='nagios-plugins-perl', version='2.3.3',
                     release='2.el7'),
                dict(name='nagios-plugins-http', version='2.3.3',
                     release='2.el7')
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._get_available_packages')
    @mock.patch('argo_poem_tools.packages.Packages._get_installed_packages')
    def test_get_analyzed_packages_all_ok(self, mock_rpmdb, mock_yumdb):
        mock_rpmdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='3.el7'),
            dict(name='nagios-plugins-globus', version='0.1.5',
                 release='20200713050450.eb1e7d8.el7'),
            dict(name='nagios-plugins-argo', version='0.1.12',
                 release='20200401115402.f599b1b.el7')
        ]
        mock_yumdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.5.0',
                 release='20191003144427.7acfd49.el7'),
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='3.el7'),
            dict(name='nagios-plugins-igtf', version='1.4.0',
                 release='20200713050846.f6ca58d.el7'),
            dict(name='nagios-plugins-globus', version='0.1.5',
                 release='20200713050450.eb1e7d8.el7'),
            dict(name='nagios-plugins-http', version='2.3.3', release='1.el7'),
            dict(name='nagios-plugins-argo', version='0.1.12',
                 release='20200716071827.5b8b5d6.el7')
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertEqual(
            install, [('nagios-plugins-http',)]
        )
        self.assertEqual(
            set(upgrade),
            {
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0')
                ),
                (
                    ('nagios-plugins-argo', '0.1.12'),
                )
            }
        )
        self.assertEqual(
            downgrade,
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ]
        )
        self.assertEqual(diff_ver, [])
        self.assertEqual(not_found, [])

    @mock.patch('argo_poem_tools.packages.Packages._get_available_packages')
    @mock.patch('argo_poem_tools.packages.Packages._get_installed_packages')
    def test_get_analyzed_packages_wrong_version_and_not_found(
            self, mock_rpmdb, mock_yumdb
    ):
        mock_rpmdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='1.el7'),
            dict(name='nagios-plugins-http', version='2.3.2', release='2.el7')
        ]
        mock_yumdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.5.0',
                 release='20191003144427.7acfd49.el7'),
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='1.el7'),
            dict(name='nagios-plugins-igtf', version='1.4.0', release='3.el7'),
            dict(name='nagios-plugins-globus', version='0.1.6',
                 release='20200713050450.eb1e7d8.el7'),
            dict(name='nagios-plugins-http', version='2.3.3', release='1.el7')
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertEqual(install, [])
        self.assertEqual(
            set(upgrade),
            {
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0')
                ),
                (
                    ('nagios-plugins-http',),
                )
            }

        )
        self.assertEqual(
            downgrade,
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ]
        )
        self.assertEqual(diff_ver, ['nagios-plugins-globus-0.1.5'])
        self.assertEqual(not_found, ['nagios-plugins-argo-0.1.12'])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get_available_packages')
    @mock.patch('argo_poem_tools.packages.Packages._get_installed_packages')
    def test_get_analyzed_packages_if_marked_for_upgrade_and_same_version_avail(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock_rpmdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='3.el7'),
            dict(name='nagios-plugins-globus', version='0.1.5',
                 release='20200713050450.eb1e7d8.el7'),
            dict(name='nagios-plugins-argo', version='0.1.12',
                 release='20200401115402.f99b1b.el7')
        ]
        mock_yumdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='3.el7'),
            dict(name='nagios-plugins-igtf', version='1.4.0',
                 release='20200713050846.f6ca58d.el7'),
            dict(name='nagios-plugins-globus', version='0.1.5',
                 release='20200713050450.eb1e7d8.el7'),
            dict(name='nagios-plugins-http', version='2.3.3', release='1.el7'),
            dict(name='nagios-plugins-argo', version='0.1.12',
                 release='20200401115402.f99b1b.el7'),
            dict(name='nagios-plugins-argo', version='0.1.12',
                 release='20200716071827.5b8b5d6.el7')
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertFalse(mock_sp.called)
        self.assertEqual(install, [('nagios-plugins-http',)])
        self.assertEqual(upgrade, [(('nagios-plugins-argo', '0.1.12'),)])
        self.assertEqual(
            downgrade,
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ]
        )
        self.assertEqual(diff_ver, ['nagios-plugins-fedcloud-0.5.0'])
        self.assertEqual(not_found, [])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get_available_packages')
    @mock.patch('argo_poem_tools.packages.Packages._get_installed_packages')
    def test_get_packages_if_installed_and_wrong_version_available(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock_rpmdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='1.el7'),
            dict(name='nagios-plugins-http', version='2.0.0', release='2.el7')
        ]
        mock_yumdb.return_value = [
            dict(name='nagios-plugins-fedcloud', version='0.5.0',
                 release='20191003144427.7acfd49.el7'),
            dict(name='nagios-plugins-fedcloud', version='0.4.0',
                 release='20190925233153.c3b9fdd.el7'),
            dict(name='nagios-plugins-igtf', version='1.5.0', release='1.el7'),
            dict(name='nagios-plugins-igtf', version='1.4.0', release='3.el7'),
            dict(name='nagios-plugins-globus', version='0.1.6',
                 release='20200713050450.eb1e7d8.el7'),
            dict(name='nagios-plugins-http', version='2.3.3', release='1.el7'),
            dict(name='nagios-plugins-argo', version='0.1.12',
                 release='20200716071827.5b8b5d6.el7')
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertFalse(mock_sp.called)
        self.assertEqual(install, [('nagios-plugins-argo', '0.1.12')])
        self.assertEqual(
            set(upgrade),
            {
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0')
                ),
                (('nagios-plugins-http',),)
            }
        )
        self.assertEqual(
            downgrade,
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ]
        )
        self.assertEqual(diff_ver, ['nagios-plugins-globus-0.1.5'])
        self.assertEqual(not_found, [])

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_install_packages(self, mock_get, mock_check_call, mock_lock):
        mock_get.return_value = (
            [('nagios-plugins-http',)],
            [
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0'),
                ),
                (('nagios-plugins-argo', '0.1.12'),)
            ],
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ],
            [],
            []
        )
        mock_check_call.side_effect = mock_func
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_check_call.call_count, 4)
        mock_check_call.assert_has_calls([
            mock.call(
                ['yum', '-y', 'install', 'nagios-plugins-fedcloud-0.5.0']
            ),
            mock.call(['yum', '-y', 'downgrade', 'nagios-plugins-igtf-1.4.0']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-http']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-argo-0.1.12']),
        ], any_order=True)
        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(
            info,
            [
                'Packages installed: nagios-plugins-http',
                'Packages upgraded: '
                'nagios-plugins-fedcloud-0.4.0 -> '
                'nagios-plugins-fedcloud-0.5.0; nagios-plugins-argo-0.1.12',
                'Packages downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0'
            ]
        )
        self.assertEqual(warn, [])

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_install_packages_if_installed_and_wrong_version_available(
            self, mock_get, mock_check_call, mock_lock
    ):
        mock_get.return_value = (
            [('nagios-plugins-argo', '0.1.12')],
            [
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0'),
                ),
                (('nagios-plugins-http',),)
            ],
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ],
            ['nagios-plugins-globus-0.1.5'],
            []
        )
        mock_check_call.side_effect = mock_func
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_check_call.call_count, 4)
        self.assertEqual(mock_lock.call_count, 1)
        mock_check_call.assert_has_calls([
            mock.call(
                ['yum', '-y', 'install', 'nagios-plugins-fedcloud-0.5.0']
            ),
            mock.call(['yum', '-y', 'downgrade', 'nagios-plugins-igtf-1.4.0']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-http']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-argo-0.1.12'])
        ], any_order=True)
        self.assertEqual(
            info,
            [
                'Packages installed: nagios-plugins-argo-0.1.12',
                'Packages upgraded: '
                'nagios-plugins-fedcloud-0.4.0 -> nagios-plugins-fedcloud-'
                '0.5.0; nagios-plugins-http',
                'Packages downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0',
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found with requested version: '
                'nagios-plugins-globus-0.1.5'
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_install_if_packages_not_found(
            self, mock_get, mock_check_call, mock_lock
    ):
        mock_get.return_value = (
            [('nagios-plugins-igtf', '1.4.0')],
            [],
            [],
            ['nagios-plugins-fedcloud-0.5.0'],
            ['nagios-plugins-globus-0.1.5', 'nagios-plugins-argo-0.1.12',
             'nagios-plugins-http']
        )
        mock_check_call.side_effect = mock_func
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_check_call.call_count, 1)
        self.assertEqual(mock_lock.call_count, 1)
        mock_check_call.assert_has_calls([
            mock.call(['yum', '-y', 'install', 'nagios-plugins-igtf-1.4.0']),
        ], any_order=True)
        self.assertEqual(
            info, ['Packages installed: nagios-plugins-igtf-1.4.0']
        )
        self.assertEqual(
            warn,
            [
                'Packages not found with requested version: '
                'nagios-plugins-fedcloud-0.5.0',
                'Packages not found: '
                'nagios-plugins-globus-0.1.5; nagios-plugins-argo-0.1.12; '
                'nagios-plugins-http'
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_install_if_packages_marked_for_upgrade_and_same_version_avail(
            self, mock_get, mock_check_call, mock_lock
    ):
        mock_get.return_value = (
            [('nagios-plugins-http', )],
            [(('nagios-plugins-argo', '0.1.12'),)],
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ],
            ['nagios-plugins-fedcloud-0.5.0'],
            []
        )
        mock_check_call.side_effect = mock_func
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_check_call.call_count, 3)
        mock_check_call.assert_has_calls([
            mock.call(['yum', '-y', 'install', 'nagios-plugins-http']),
            mock.call(['yum', '-y', 'downgrade', 'nagios-plugins-igtf-1.4.0']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-argo-0.1.12'])
        ], any_order=True)
        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(
            info,
            [
                'Packages installed: nagios-plugins-http',
                'Packages upgraded: nagios-plugins-argo-0.1.12',
                'Packages downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0'
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found with requested version: '
                'nagios-plugins-fedcloud-0.5.0'
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._failsafe_lock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_install_lock_versions_if_exception(
            self, mock_get, mock_check_call, mock_lock
    ):
        self.pkgs.initially_locked_versions = [
            'nagios-plugins-argo', 'nagios-plugins-fedcloud'
        ]
        mock_get.side_effect = mock_func_exception
        mock_check_call.side_effect = mock_func
        mock_lock.side_effect = mock_func
        with self.assertRaises(PackageException):
            self.pkgs.install()
        self.assertFalse(mock_check_call.called)
        self.assertEqual(mock_lock.call_count, 1)

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_no_op_run(self, mock_get, mock_lock):
        self.pkgs.versions_unlocked = True
        self.pkgs.locked_versions = [
            'nagios-plugins-argo', 'nagios-plugins-igtf'
        ]
        mock_get.return_value = (
            [('nagios-plugins-http', )],
            [
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0'),
                ),
                (('nagios-plugins-argo', '0.1.12'),)
            ],
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ],
            [],
            []
        )
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.no_op()
        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-http',
                'Packages to be upgraded: '
                'nagios-plugins-fedcloud-0.4.0 -> '
                'nagios-plugins-fedcloud-0.5.0; nagios-plugins-argo-0.1.12',
                'Packages to be downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0'
            ]
        )
        self.assertEqual(warn, [])

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_no_op_if_installed_and_wrong_version_available(
            self, mock_get, mock_lock
    ):
        self.pkgs.versions_unlocked = True
        self.pkgs.locked_versions = ['nagios-plugins-fedcloud']
        mock_get.return_value = (
            [('nagios-plugins-argo', '0.1.12')],
            [
                (
                    ('nagios-plugins-fedcloud', '0.4.0'),
                    ('nagios-plugins-fedcloud', '0.5.0'),
                ),
                (('nagios-plugins-http', ),)
            ],
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ],
            ['nagios-plugins-globus-0.1.5'],
            []
        )
        info, warn = self.pkgs.no_op()
        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-argo-0.1.12',
                'Packages to be upgraded: '
                'nagios-plugins-fedcloud-0.4.0 -> nagios-plugins-fedcloud-'
                '0.5.0; nagios-plugins-http',
                'Packages to be downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0',
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found with requested version: '
                'nagios-plugins-globus-0.1.5'
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_no_op_if_packages_not_found(self, mock_get, mock_lock):
        mock_get.return_value = (
            [('nagios-plugins-igtf', '1.4.0')],
            [],
            [],
            ['nagios-plugins-fedcloud-0.5.0'],
            ['nagios-plugins-globus-0.1.5', 'nagios-plugins-argo-0.1.12',
             'nagios-plugins-http']
        )
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.no_op()
        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-igtf-1.4.0'
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found with requested version: '
                'nagios-plugins-fedcloud-0.5.0',
                'Packages not found: '
                'nagios-plugins-globus-0.1.5; nagios-plugins-argo-0.1.12; '
                'nagios-plugins-http'
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._lock_versions')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_no_op_if_packages_marked_for_upgrade_and_same_version_avail(
            self, mock_get, mock_lock
    ):
        mock_get.return_value = (
            [('nagios-plugins-http', )],
            [(('nagios-plugins-argo', '0.1.12'), )],
            [
                (
                    ('nagios-plugins-igtf', '1.5.0'),
                    ('nagios-plugins-igtf', '1.4.0')
                )
            ],
            ['nagios-plugins-fedcloud-0.5.0'],
            []
        )
        mock_lock.side_effect = mock_func
        info, warn = self.pkgs.no_op()
        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-http',
                'Packages to be upgraded: nagios-plugins-argo-0.1.12',
                'Packages to be downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0'
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found with requested version: '
                'nagios-plugins-fedcloud-0.5.0'
            ]
        )

    @mock.patch('argo_poem_tools.packages.Packages._failsafe_lock_versions')
    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.Packages._get')
    def test_no_op_lock_versions_if_exception(
            self, mock_get, mock_check_call, mock_lock
    ):
        self.pkgs.initially_locked_versions = [
            'nagios-plugins-argo', 'nagios-plugins-fedcloud'
        ]
        mock_get.side_effect = mock_func_exception
        mock_check_call.side_effect = mock_func
        mock_lock.side_effect = mock_func
        with self.assertRaises(PackageException):
            self.pkgs.no_op()
        self.assertFalse(mock_check_call.called)
        self.assertEqual(mock_lock.call_count, 1)

    @mock.patch('argo_poem_tools.packages.subprocess.call')
    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_lock_unlocked_versions(self, mock_subprocess, mock_call):
        mock_subprocess.side_effect = [mock_yum_versionlock_list, mock_rpm_qa]
        mock_call.side_effect = mock_func
        warn = self.pkgs._lock_versions()
        self.assertFalse(warn)
        self.assertEqual(mock_call.call_count, 1)
        mock_call.assert_has_calls([
            mock.call(
                ['yum', 'versionlock', 'add', 'nagios-plugins-igtf'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        ], any_order=True)

    @mock.patch('argo_poem_tools.packages.subprocess.call')
    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_lock_unlocked_versions_if_package_not_installed(
            self, mock_subprocess, mock_call
    ):
        mock_rpm_qa1 = \
            """
            nagios-plugins-2.3.3-2.el7.x86_64
            nagios-plugins-file_age-2.3.3-2.el7.x86_64
            nagios-plugins-argo-0.1.13-20200901060701.5869b94.el7.noarch
            nagios-plugins-fedcloud-0.5.2-20200511071632.05e2501.el7.noarch
            nagios-plugins-dummy-2.3.3-2.el7.x86_64
            nagios-common-4.4.5-7.el7.x86_64
            nagios-plugins-perl-2.3.3-2.el7.x86_64
            nagios-plugins-http-2.3.3-2.el7.x86_64
    
            """.encode('utf-8')
        mock_subprocess.side_effect = [mock_yum_versionlock_list, mock_rpm_qa1]
        mock_call.side_effect = mock_func
        warn = self.pkgs._lock_versions()
        self.assertFalse(warn)
        self.assertEqual(mock_call.call_count, 0)

    @mock.patch('argo_poem_tools.packages.subprocess.call')
    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_lock_unlocked_versions_exception(self, mock_subprocess, mock_call):
        mock_subprocess.side_effect = [mock_yum_versionlock_list, mock_rpm_qa]
        mock_call.side_effect = mock_func_exception
        warn = self.pkgs._lock_versions()
        self.assertEqual(mock_call.call_count, 1)
        mock_call.assert_has_calls([
            mock.call(
                ['yum', 'versionlock', 'add', 'nagios-plugins-igtf'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        ], any_order=True)
        self.assertEqual(warn, 'Packages not locked: nagios-plugins-igtf')
