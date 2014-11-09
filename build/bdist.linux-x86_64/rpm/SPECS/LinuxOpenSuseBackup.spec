%define name python27-linuxopensusebackup
%define pythonname LinuxOpenSuseBackup
%define version 1.0
%define unmangled_version 1.0
%define release 1

%define __os_install_post\
%( rpm --eval %%__os_install_post)\
( cd $RPM_BUILD_ROOT; find . -type f | sed -e 's/^.//') > INSTALLED_FILES
Summary: Python Distribution Utilities
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{pythonname}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{pythonname}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Greg Ward <gward@python.net>
Url: http://www.python.org/sigs/distutils-sig/

%description
UNKNOWN

%prep
%setup -n %{pythonname}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
