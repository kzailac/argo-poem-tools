#!/usr/bin/python
import unittest
from unittest import mock

from argo_poem_tools.packages import Packages, _compare_versions, _compare_vr

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

""".encode('utf-8')


def mock_func(*args, **kwargs):
    pass


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
        self.assertEqual(_compare_vr(('0.0.1', '1.el7'), ('1.0.0', '2.el7')), -1)
        self.assertEqual(_compare_vr(('2.0.1', '1.el7'), ('1.0.0', '2.el7')), 1)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.pkgs = Packages(data)

    def test_get_package_list(self):
        self.assertEqual(
            self.pkgs.package_list,
            [
                ('nagios-plugins-fedcloud', '0.5.0'),
                ('nagios-plugins-igtf', '1.4.0'),
                ('nagios-plugins-globus', '0.1.5'),
                ('nagios-plugins-argo', '0.1.12'),
                ('nagios-plugins-http', )
            ]
        )

    @mock.patch('argo_poem_tools.packages.subprocess.check_output')
    def test_get_available_packages(self, mock_yumdb):
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
                     release='20200713050609.a481696.el7')
            ]
        )

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
            self.pkgs.packages_not_found,
            [
                ('nagios-plugins-globus', '0.1.5'),
                ('nagios-plugins-argo', '0.1.12')
            ]
        )

    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_get_analyzed_packages_all_ok(self, mock_rpmdb, mock_yumdb):
        mock1 = mock.Mock(version='0.5.0', release='20191003144427.7acfd49.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock3 = mock.Mock(version='1.5.0', release='3.el6')
        mock4 = mock.Mock(version='1.4.0', release='20200713050846.f6ca58d.el6')
        mock5 = mock.Mock(version='0.1.5', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(
            version='0.1.12', release='20200401115402.f599b1b.el6'
        )
        mock8 = mock.Mock(
            version='0.1.12', release='20200716071827.5b8b5d6.el6'
        )
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-argo'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock5, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock8
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertEqual(
            install, ['nagios-plugins-http']
        )
        self.assertEqual(
            upgrade,
            [
                ('nagios-plugins-fedcloud-0.4.0',
                 'nagios-plugins-fedcloud-0.5.0'),
                ('nagios-plugins-argo-0.1.12',)
            ]
        )
        self.assertEqual(
            downgrade,
            [('nagios-plugins-igtf-1.5.0', 'nagios-plugins-igtf-1.4.0')]
        )
        self.assertEqual(diff_ver, [])
        self.assertEqual(not_found, [])

    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_get_analyzed_packages_wrong_version_and_not_found(
            self, mock_rpmdb, mock_yumdb
    ):
        mock1 = mock.Mock(version='0.5.0', release='20191003144427.7acfd49.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock3 = mock.Mock(version='1.5.0', release='1.el6')
        mock4 = mock.Mock(version='1.4.0', release='3.el6')
        mock5 = mock.Mock(version='0.1.6', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(version='2.3.2', release='2.el6')
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-http'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertEqual(install, [])
        self.assertEqual(
            upgrade,
            [('nagios-plugins-http',),
             ('nagios-plugins-fedcloud-0.4.0', 'nagios-plugins-fedcloud-0.5.0')]
        )
        self.assertEqual(
            downgrade,
            [('nagios-plugins-igtf-1.5.0', 'nagios-plugins-igtf-1.4.0')]
        )
        self.assertEqual(
            diff_ver,
            [('nagios-plugins-globus-0.1.5', 'nagios-plugins-globus-0.1.6')]
        )
        self.assertEqual(not_found, ['nagios-plugins-argo-0.1.12'])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_get_analyzed_packages_if_marked_for_upgrade_and_same_version_avail(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock1 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock2 = mock.Mock(version='1.5.0', release='3.el6')
        mock3 = mock.Mock(version='1.4.0', release='20200713050846.f6ca58d.el6')
        mock4 = mock.Mock(version='0.1.5', release='20200713050450.eb1e7d8.el6')
        mock5 = mock.Mock(version='2.3.3', release='1.el6')
        mock6 = mock.Mock(
            version='0.1.12', release='20200401115402.f99b1b.el6'
        )
        mock7 = mock.Mock(
            version='0.1.12', release='20200716071827.5b8b5d6.el6'
        )
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-igtf'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-globus'
        mock5.name = 'nagios-plugins-http'
        mock6.name = 'nagios-plugins-argo'
        mock7.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock1, mock2, mock4, mock6]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock7
        ]
        install, upgrade, downgrade, diff_ver, not_found = self.pkgs._get()
        self.assertFalse(mock_sp.called)
        self.assertEqual(install, ['nagios-plugins-http'])
        self.assertEqual(upgrade, [('nagios-plugins-argo-0.1.12', )])
        self.assertEqual(
            downgrade,
            [('nagios-plugins-igtf-1.5.0', 'nagios-plugins-igtf-1.4.0')]
        )
        self.assertEqual(diff_ver, [])
        self.assertEqual(not_found, [])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_install_packages(self, mock_rpmdb, mock_yumdb, mock_sp):
        mock1 = mock.Mock(version='0.5.0', release='20191003144427.7acfd49.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock3 = mock.Mock(version='1.5.0', release='3.el6')
        mock4 = mock.Mock(version='1.4.0', release='20200713050846.f6ca58d.el6')
        mock5 = mock.Mock(version='0.1.5', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(
            version='0.1.12', release='20200401115402.f599b1b.el6'
        )
        mock8 = mock.Mock(
            version='0.1.12', release='20200716071827.5b8b5d6.el6'
        )
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-argo'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock5, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock8
        ]
        mock_sp.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_sp.call_count, 4)
        mock_sp.assert_has_calls([
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
                'Packages installed: nagios-plugins-http',
                'Packages upgraded: '
                'nagios-plugins-fedcloud-0.4.0 -> '
                'nagios-plugins-fedcloud-0.5.0; nagios-plugins-argo-0.1.12',
                'Packages downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0'
            ]
        )
        self.assertEqual(warn, [])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_install_packages_if_installed_and_wrong_version_available(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock1 = mock.Mock(version='0.5.0', release='20191003144427.7acfd49.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock3 = mock.Mock(version='1.5.0', release='1.el6')
        mock4 = mock.Mock(version='1.4.0', release='3.el6')
        mock5 = mock.Mock(version='0.1.6', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(version='2.0.0', release='2.el6')
        mock8 = mock.Mock(version='0.1.12', release='20200716071827.5b8b5d6.el6')
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-http'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock8
        ]
        mock_sp.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_sp.call_count, 5)
        mock_sp.assert_has_calls([
            mock.call(
                ['yum', '-y', 'install', 'nagios-plugins-fedcloud-0.5.0']
            ),
            mock.call(['yum', '-y', 'downgrade', 'nagios-plugins-igtf-1.4.0']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-globus-0.1.6']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-http']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-argo-0.1.12'])
        ], any_order=True)
        self.assertEqual(
            info,
            [
                'Packages installed: nagios-plugins-argo-0.1.12',
                'Packages upgraded: nagios-plugins-http; '
                'nagios-plugins-fedcloud-0.4.0 -> nagios-plugins-fedcloud-'
                '0.5.0',
                'Packages downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0',
                'Packages installed with different version: '
                'nagios-plugins-globus-0.1.5 -> nagios-plugins-globus-0.1.6'
            ]
        )
        self.assertEqual(warn, [])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_install_if_packages_not_found(
            self, mock_rpmdb, mock_yumbd, mock_sp
    ):
        mock1 = mock.Mock(version='0.6.0', release='20200511071632.05e2501.el6')
        mock2 = mock.Mock(version='1.4.0', release='3.el6')
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-igtf'
        mock_rpmdb.returnPackages.return_value = []
        mock_yumbd.returnPackages.return_value = [mock1, mock2]
        mock_sp.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_sp.call_count, 2)
        mock_sp.assert_has_calls([
            mock.call(
                ['yum', '-y', 'install', 'nagios-plugins-fedcloud-0.6.0']
            ),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-igtf-1.4.0'])
        ], any_order=True)
        self.assertEqual(
            info,
            [
                'Packages installed: nagios-plugins-igtf-1.4.0',
                'Packages installed with different version: '
                'nagios-plugins-fedcloud-0.5.0 -> nagios-plugins-fedcloud-0.6.0'
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found: nagios-plugins-http; '
                'nagios-plugins-globus-0.1.5; nagios-plugins-argo-0.1.12'
            ]
        )

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_install_if_packages_marked_for_upgrade_and_same_version_avail(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock1 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190917114007.10e7e8f.el6')
        mock3 = mock.Mock(version='1.5.0', release='3.el6')
        mock4 = mock.Mock(version='1.4.0', release='20200713050846.f6ca58d.el6')
        mock5 = mock.Mock(version='0.1.5', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(
            version='0.1.12', release='20200401115402.f99b1b.el6'
        )
        mock8 = mock.Mock(
            version='0.1.12', release='20200716071827.5b8b5d6.el6'
        )
        mock1.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-argo'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock5, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock7, mock8
        ]
        mock_sp.side_effect = mock_func
        info, warn = self.pkgs.install()
        self.assertEqual(mock_sp.call_count, 4)
        mock_sp.assert_has_calls([
            mock.call(['yum', '-y', 'install', 'nagios-plugins-http']),
            mock.call(['yum', '-y', 'downgrade', 'nagios-plugins-igtf-1.4.0']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-argo-0.1.12']),
            mock.call(['yum', '-y', 'install', 'nagios-plugins-fedcloud-0.4.0'])
        ], any_order=True)
        self.assertEqual(
            info,
            [
                'Packages installed: nagios-plugins-http',
                'Packages upgraded: nagios-plugins-argo-0.1.12',
                'Packages downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0',
                'Packages installed with different version: '
                'nagios-plugins-fedcloud-0.5.0 -> nagios-plugins-fedcloud-0.4.0'
            ]
        )
        self.assertEqual(warn, [])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_no_op_run(self, mock_rpmdb, mock_yumdb, mock_sp):
        mock1 = mock.Mock(version='0.5.0', release='20191003144427.7acfd49.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock3 = mock.Mock(version='1.5.0', release='3.el6')
        mock4 = mock.Mock(version='1.4.0', release='20200713050846.f6ca58d.el6')
        mock5 = mock.Mock(version='0.1.5', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(
            version='0.1.12', release='20200401115402.f599b1b.el6'
        )
        mock8 = mock.Mock(
            version='0.1.12', release='20200716071827.5b8b5d6.el6'
        )
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-argo'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock5, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock8
        ]
        mock_sp.side_effect = mock_func
        info, warn = self.pkgs.no_op()
        self.assertFalse(mock_sp.called)
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

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_no_op_if_installed_and_wrong_version_available(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock1 = mock.Mock(version='0.5.0', release='20191003144427.7acfd49.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock3 = mock.Mock(version='1.5.0', release='1.el6')
        mock4 = mock.Mock(version='1.4.0', release='3.el6')
        mock5 = mock.Mock(version='0.1.6', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(version='2.0.0', release='5.el6')
        mock8 = mock.Mock(version='0.1.12', release='20200716071827.5b8b5d6.el6')
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-http'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock8
        ]
        info, warn = self.pkgs.no_op()
        self.assertFalse(mock_sp.called)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-argo-0.1.12',
                'Packages to be upgraded: nagios-plugins-http; '
                'nagios-plugins-fedcloud-0.4.0 -> nagios-plugins-fedcloud-'
                '0.5.0',
                'Packages to be downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0',
                'Packages to be installed with different version: '
                'nagios-plugins-globus-0.1.5 -> nagios-plugins-globus-0.1.6'
            ]
        )
        self.assertEqual(warn, [])

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_no_op_if_packages_not_found(self, mock_rpmdb, mock_yumbd, mock_sp):
        mock1 = mock.Mock(version='0.6.0', release='20200511071632.05e2501.el6')
        mock2 = mock.Mock(version='1.4.0', release='3.el6')
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-igtf'
        mock_rpmdb.returnPackages.return_value = []
        mock_yumbd.returnPackages.return_value = [mock1, mock2]
        info, warn = self.pkgs.no_op()
        self.assertFalse(mock_sp.called)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-igtf-1.4.0',
                'Packages to be installed with different version: '
                'nagios-plugins-fedcloud-0.5.0 -> nagios-plugins-fedcloud-0.6.0'
            ]
        )
        self.assertEqual(
            warn,
            [
                'Packages not found: nagios-plugins-http; '
                'nagios-plugins-globus-0.1.5; nagios-plugins-argo-0.1.12'
            ]
        )

    @mock.patch('argo_poem_tools.packages.subprocess.check_call')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_no_op_if_packages_marked_for_upgrade_and_same_version_avail(
            self, mock_rpmdb, mock_yumdb, mock_sp
    ):
        mock1 = mock.Mock(version='0.4.0', release='20190925233153.c3b9fdd.el6')
        mock2 = mock.Mock(version='0.4.0', release='20190917114007.10e7e8f.el6')
        mock3 = mock.Mock(version='1.5.0', release='3.el6')
        mock4 = mock.Mock(version='1.4.0', release='20200713050846.f6ca58d.el6')
        mock5 = mock.Mock(version='0.1.5', release='20200713050450.eb1e7d8.el6')
        mock6 = mock.Mock(version='2.3.3', release='1.el6')
        mock7 = mock.Mock(
            version='0.1.12', release='20200401115402.f99b1b.el6'
        )
        mock8 = mock.Mock(
            version='0.1.12', release='20200716071827.5b8b5d6.el6'
        )
        mock1.name = 'nagios-plugins-fedcloud'
        mock3.name = 'nagios-plugins-igtf'
        mock4.name = 'nagios-plugins-igtf'
        mock5.name = 'nagios-plugins-globus'
        mock6.name = 'nagios-plugins-http'
        mock7.name = 'nagios-plugins-argo'
        mock8.name = 'nagios-plugins-argo'
        mock_rpmdb.returnPackages.return_value = [mock2, mock3, mock5, mock7]
        mock_yumdb.returnPackages.return_value = [
            mock1, mock2, mock3, mock4, mock5, mock6, mock7, mock8
        ]
        info, warn = self.pkgs.no_op()
        self.assertFalse(mock_sp.called)
        self.assertEqual(
            info,
            [
                'Packages to be installed: nagios-plugins-http',
                'Packages to be upgraded: nagios-plugins-argo-0.1.12',
                'Packages to be downgraded: '
                'nagios-plugins-igtf-1.5.0 -> nagios-plugins-igtf-1.4.0',
                'Packages to be installed with different version: '
                'nagios-plugins-fedcloud-0.5.0 -> nagios-plugins-fedcloud-0.4.0'
            ]
        )
        self.assertEqual(warn, [])


if __name__ == '__main__':
    unittest.main()
