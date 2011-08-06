Summary: Tool to gather system statistics and submit them to a central server
Name: systory-client
Version: 1.4
Release: 1%{?dist}
Group: Applications/System
License: Artistic
URL: http://www.stanford.edu/~ssklar/systory/
Obsoletes: systory
BuildArch: noarch

Source0: http://www.stanford.edu/~ssklar/systory/systory-client-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
systory-client is a perl script that runs through cron and transmits its data
to a collection server for the display of graphs related to the system's historical
performance.

%prep
%setup -q

%build

%install
%{__rm} -rf %{buildroot}
%{__install} -Dpm 0755 systory-client %{buildroot}%{_bindir}/systory-client
%{__install} -Dpm 0644 systory-client.cron  %{buildroot}/etc/cron.d/systory-client.cron

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%{_bindir}/systory-client
/etc/cron.d/systory-client.cron

%changelog
* Sat Aug 06 2011 Sandor W Sklar <ssklar@stanford.edu> 1.4-1
- Update spec file for client version 1.4
* Tue Mar 23 2010 Sandor W Sklar <ssklar@stanford.edu> 1.3-1
- Initial package.
