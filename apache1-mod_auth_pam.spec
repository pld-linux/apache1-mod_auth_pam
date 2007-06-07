%define		mod_name	auth_pam
%define 	apxs		/usr/sbin/apxs1
Summary:	This is the PAM authentication module for Apache
Summary(es.UTF-8):	Este módulo proporciona autenticación PAM para Apache
Summary(pl.UTF-8):	Moduł uwierzytelnienia PAM dla Apache
Summary(pt_BR.UTF-8):	Este módulo provê autenticação PAM para o Apache
Name:		apache1-mod_%{mod_name}
Version:	1.1.1
Release:	5
License:	GPL
Group:		Networking/Daemons
Source0:	http://pam.sourceforge.net/mod_auth_pam/dist/mod_%{mod_name}-%{version}.tar.gz
# Source0-md5:	b1e36b5df18a177e671785f7f4c8001c
Patch0:		%{name}-symbol_fix.patch
Patch1:		%{name}-broken_lines.patch
URL:		http://pam.sourceforge.net/mod_auth_pam/
BuildRequires:	apache1-apxs
BuildRequires:	apache1-devel >= 1.3.33-2
BuildRequires:	pam-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(triggerpostun):	%{apxs}
Requires:	apache1(EAPI)
Obsoletes:	apache-mod_auth_pam <= 1.1.1-4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
This is an authentication module for Apache that allows you to
authenticate HTTP clients using PAM (pluggable authentication module).

%description -l es.UTF-8
Este módulo permite autenticar clientes HTTP usando el directorio PAM.

%description -l pl.UTF-8
To jest moduł uwierzytelnienia dla Apache pozwalający na
uwierzytelnianie klientów HTTP przez PAM.

%description -l pt_BR.UTF-8
Este módulo permite que você autentique clientes HTTP usando o
diretório PAM.

%prep
%setup -q -n mod_%{mod_name}-%{version}
%patch0 -p1
%patch1 -p0

%build
%{apxs} -c mod_%{mod_name}.c -o mod_%{mod_name}.so -lpam -ldl

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/conf.d,/etc/pam.d}

install mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install samples/httpd- $RPM_BUILD_ROOT/etc/pam.d/httpd

echo 'LoadModule %{mod_name}_module	modules/mod_%{mod_name}.so' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod_%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q apache restart

%postun
if [ "$1" = "0" ]; then
	%service -q apache restart
fi

%triggerpostun -- apache1-mod_%{mod_name} < 1.1.1-3.1
# check that they're not using old apache.conf
if grep -q '^Include conf\.d' /etc/apache/apache.conf; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
fi

%files
%defattr(644,root,root,755)
%doc doc/{configure,faq}.txt samples/dot-htaccess README
%config(noreplace) /etc/pam.d/httpd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*
