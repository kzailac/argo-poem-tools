#!/usr/bin/python
import unittest

import mock
from argo_poem_tools.packages import Packages

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
                   "name=Extra Packages for Enterprise Linux 6 - $basearch\n"
                   "mirrorlist=https://mirrors.fedoraproject.org/metalink?"
                   "repo=epel-6&arch=$basearch\n"
                   "failovermethod=priority\n"
                   "enabled=1\n"
                   "gpgcheck=1\n"
                   "gpgkey=https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-"
                   "EPEL-6",
        "packages": [
            {
                "name": "nagios-plugins-http",
                "version": "present"
            }
        ]
    }
}


def mock_func(*args, **kwargs):
    pass


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.pkgs = Packages(data)

    def test_get_package_list(self):
        self.assertEqual(
            self.pkgs.package_list,
            [
                ('nagios-plugins-http',),
                ('nagios-plugins-fedcloud', '0.5.0'),
                ('nagios-plugins-igtf', '1.4.0'),
                ('nagios-plugins-globus', '0.1.5'),
                ('nagios-plugins-argo', '0.1.12')
            ]
        )

    @mock.patch('argo_poem_tools.packages.yum.YumBase.pkgSack')
    @mock.patch('argo_poem_tools.packages.yum.YumBase.rpmdb')
    def test_get_exceptions(self, mock_rpmdb, mock_yumdb):
        mock1 = mock.Mock(version='0.6.0', release='20200511071632.05e2501.el6')
        mock2 = mock.Mock(version='1.4.0', release='3.el6')
        mock3 = mock.Mock(version='2.3.3', release='1.el6')
        mock1.name = 'nagios-plugins-fedcloud'
        mock2.name = 'nagios-plugins-igtf'
        mock3.name = 'nagios-plugins-http'
        mock_rpmdb.returnPackages.return_value = []
        mock_yumdb.returnPackages.return_value = [mock1, mock2, mock3]
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
