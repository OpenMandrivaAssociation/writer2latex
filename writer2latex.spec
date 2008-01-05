%define _with_gcj_support 0
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# Magic to figure ooodir:
%define ooo_version %(rpm -q --qf '%%{version}' %{ooname}-java-common 2>/dev/null)
%define ooo_shortver %(echo %ooo_version | perl -p -e 's/^([^\\\.]+\\\.[^\\\.]+)\\\..*/\\\1/')
%define ooodir %{_libdir}/ooo-%{ooo_shortver}
%define ooname openoffice.org
%ifarch x86_64
%define ooname openoffice.org64
%define ooodir %{_libdir}/ooo-%{ooo_shortver}_64
%endif

Name:          writer2latex
Version:       0.5
Release:       %mkrel 1
Summary:       Writer2LateX Document Converter
License:       LGPLv2
Url:           http://www.hj-gym.dk/~hj/writer2latex/
Source0:       http://www.hj-gym.dk/~hj/writer2latex/writer2latex05.zip
Patch0:        writer2latex05.rh.patch
BuildRequires: java-rpmbuild
BuildRequires: openoffice.org-java-common
BuildRequires: ant
Group:         Text Processing/Markup/XML
%if ! %{gcj_support}
Buildarch:     noarch
%endif
Buildroot:     %{_tmppath}/%{name}-%{version}-%{release}-builroot
Requires:      xalan-j2, xerces-j2

%if %{gcj_support}
BuildRequires: java-gcj-compat-devel
%endif

%description
Writer2LaTeX is a utility written in java. It converts OpenOffice.org documents
– in particular documents containing formulas – into other formats. It is
actually a collection of four converters, i.e.:
1) Writer2LaTeX converts documents into LaTeX 2e format for high quality
   typesetting.
2) Writer2BibTeX extracts bibliographic data from a document and stores it in
   BibTeX format (works together with Writer2LaTeX).
3) Writer2xhtml converts documents into XHTML 1.0 or XHTML 1.1+MathML 2.0 with
   CSS2.
4) Calc2xhtml is a companion to Writer2xhtml that converts OOo Calc documents
   to XHTML 1.0 with CSS2 to display your spreadsheets on the web.

%package javadoc
Summary:     Javadoc for %{name}
Group:       Development/Documentation

%description javadoc
Javadoc for %{name}.

%package -n openoffice.org-%{name}
Summary:          OpenOffice.org Writer2LateX Extension
Group:            Applications/Productivity
Requires:         openoffice.org-common
Requires(pre):    openoffice.org-common
Requires(post):   openoffice.org-common
Requires(preun):  openoffice.org-common
Requires(postun): openoffice.org-common


%description -n openoffice.org-%{name}
Document Converter Extension for OpenOffice.org to provide
XHTML, LaTeX and BibTeX export filters.

%prep
%setup -q -n writer2latex05
%patch0 -p1 -b .rh.patch
sed -i -e "s#LIBDIR#%{_libdir}#" build.xml

%build
%ant jar javadoc package -DOFFICE_HOME="%{ooodir}"

%install
rm -rf $RPM_BUILD_ROOT
# jar
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 target/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} ${jar/-%{version}/}; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -r target/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
pushd $RPM_BUILD_ROOT%{_javadocdir}
ln -s %{name}-%{version} %{name}
popd
# OOo extension
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/writer2latex.uno.pkg
unzip target/lib/writer2latex.uno.pkg -d $RPM_BUILD_ROOT%{_datadir}/writer2latex.uno.pkg

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%pre -n openoffice.org-%{name}
if [ $1 -gt 1 ]; then
    # Upgrade => deregister old extension
    unopkg remove --shared org.openoffice.legacy.writer2latex.uno.pkg -env:JFW_PLUGIN_DO_NOT_CHECK_ACCESSIBILITY=1 > /dev/null 2>&1 || :
fi

%post -n openoffice.org-%{name}
    # register extension
    unopkg add --shared --link %{_datadir}/writer2latex.uno.pkg -env:JFW_PLUGIN_DO_NOT_CHECK_ACCESSIBILITY=1 || :

%preun -n openoffice.org-%{name}
if [ $1 -eq 0 ]; then
    # not upgrading => deregister
    unopkg remove --shared org.openoffice.legacy.writer2latex.uno.pkg -env:JFW_PLUGIN_DO_NOT_CHECK_ACCESSIBILITY=1 || :
fi

%postun -n openoffice.org-%{name}
    # clear disk cache
    unopkg list --shared -env:JFW_PLUGIN_DO_NOT_CHECK_ACCESSIBILITY=1 > /dev/null 2>&1 || :

%files
%defattr(0644,root,root,0755)
%doc COPYING.TXT Readme.txt History.txt
%{_javadir}/*
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}
%{_javadocdir}/%{name}-%{version}

%files -n openoffice.org-%{name}
%defattr(0644,root,root,0755)
%{_datadir}/writer2latex.uno.pkg
