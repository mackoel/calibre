Name:           calibre
Version:        0.6.42
Release:        1%{?dist}
Summary:        E-book converter and library management
Group:          Applications/Multimedia
License:        GPLv3
URL:            http://calibre-ebook.com/

# SourceURL: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz

# Upstream packages some unfree fonts which we cannot redistribute.
# While we're at it, also delete the liberation fonts which we already have.
#
# Download the upstream tarball and invoke this script while in the tarball's
# directory:
# ./generate-tarball.sh %{version}
Source0:        %{name}-%{version}-nofonts.tar.gz
Source1:        generate-tarball.sh
Patch0:         %{name}-manpages.patch
Patch1:         %{name}-no-update.patch
Patch2:         %{name}-cssprofiles.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python >= 2.6
BuildRequires:  python-devel >= 2.6
BuildRequires:  ImageMagick-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  qt-devel 
BuildRequires:  PyQt4-devel
BuildRequires:  poppler-qt4-devel >= 0.12
BuildRequires:  podofo-devel
BuildRequires:  desktop-file-utils
BuildRequires:  python-mechanize
BuildRequires:  python-lxml
BuildRequires:  python-dateutil
BuildRequires:  python-imaging
BuildRequires:  xdg-utils
BuildRequires:  python-BeautifulSoup

Requires:       PyQt4
Requires:       pyPdf
Requires:       python-cherrypy
Requires:       python-cssutils
Requires:       ImageMagick
Requires:       odfpy
Requires:       django-tagging
Requires:       python-lxml
Requires:       python-imaging
Requires:       python-mechanize
Requires:       python-dateutil
Requires:       python-genshi
Requires:       python-BeautifulSoup

%description
Calibre is meant to be a complete e-library solution. It includes library
management, format conversion, news feeds to ebook conversion as well as
e-book reader sync features.

Calibre is primarily a ebook cataloging program. It manages your ebook
collection for you. It is designed around the concept of the logical book,
i.e. a single entry in the database that may correspond to ebooks in several
formats. It also supports conversion to and from a dozen different ebook
formats.

Supported input formats are: MOBI, LIT, PRC, EPUB, ODT, HTML, CBR, CBZ, RTF,
TXT, PDF and LRS.

%prep
%setup -q -n %{name}

# don't append calibre1 to the name of the manpages. No need to compress either
# upstream won't fix: http://bugs.calibre-ebook.com/ticket/3770#comment:7
%patch0 -p1 -b .manpages

# don't check for new upstream version (that's what packagers do)
%patch1 -p1 -b .no-update

# we've moved the profiles so we don't have to redistribute cssutils
# until 0.9.6 comes to fedora
%patch2 -p1 -b .cssprofiles

# dos2unix newline conversion
%{__sed} -i 's/\r//' src/calibre/web/feeds/recipes/*

# remove shebangs
%{__sed} -i -e '/^#!\//, 1d' src/calibre/*/*/*/*.py
%{__sed} -i -e '/^#!\//, 1d' src/calibre/*/*/*.py
%{__sed} -i -e '/^#![ ]*\//, 1d' src/calibre/*/*.py
%{__sed} -i -e '/^#!\//, 1d' src/calibre/*.py
%{__sed} -i -e '/^#!\//, 1d' resources/recipes/*
%{__sed} -i -e '/^#!\//, 1d' resources/default_tweaks.py

%{__chmod} -x src/calibre/*/*/*/*.py
%{__chmod} -x src/calibre/*/*/*.py
%{__chmod} -x src/calibre/*/*.py
%{__chmod} -x src/calibre/*.py
%{__chmod} -x resources/recipes/*

%build
OVERRIDE_CFLAGS="%{optflags}" python setup.py build 

%install
rm -rf %{buildroot}

# this is the only file we need from the provided cssutils package
cp -p src/cssutils/profiles.py src/calibre/css_profiles.py

mkdir -p %{buildroot}%{_datadir}

# create directories for xdg-utils
mkdir -p %{buildroot}%{_datadir}/icons
mkdir -p %{buildroot}%{_datadir}/icons/hicolor
mkdir -p %{buildroot}%{_datadir}/packages
mkdir -p %{buildroot}%{_datadir}/mime
mkdir -p %{buildroot}%{_datadir}/mime/packages
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/desktop-directories

XDG_DATA_DIRS="%{buildroot}%{_datadir}" \
XDG_UTILS_INSTALL_MODE="system" \
LIBPATH="%{_libdir}" \
python setup.py install --root=%{buildroot}%{_prefix} \
                        --prefix=%{_prefix} \
                        --libdir=%{_libdir} \
                        --staging-libdir=%{buildroot}%{_libdir} \

# icons
mkdir -p %{buildroot}%{_datadir}/pixmaps/
cp -p resources/images/library.png                \
   %{buildroot}%{_datadir}/pixmaps/%{name}-gui.png
cp -p resources/images/viewer.svg                 \
   %{buildroot}%{_datadir}/pixmaps/calibre-viewer.svg

# every file is empty here
find %{buildroot}%{_datadir}/mime -maxdepth 1 -type f|xargs rm -f 

# packages aren't allowed to register mimetypes like this
rm -f %{buildroot}%{_datadir}/applications/defaults.list

desktop-file-validate \
%{buildroot}%{_datadir}/applications/calibre-ebook-viewer.desktop
desktop-file-validate \
%{buildroot}%{_datadir}/applications/calibre-gui.desktop
desktop-file-validate \
%{buildroot}%{_datadir}/applications/calibre-lrfviewer.desktop


mv %{buildroot}%{_datadir}/mime/packages/calibre-mimetypes \
   %{buildroot}%{_datadir}/mime/packages/calibre-mimetypes.xml

# mimetype icon for lrf
rm -rf %{buildroot}%{_datadir}/icons/hicolor/128x128
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/mimetypes
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp -p resources/images/mimetypes/lrf.svg \
      %{buildroot}%{_datadir}/icons/hicolor/scalable/mimetypes/application-x-sony-bbeb.svg
cp -p resources/images/viewer.svg \
      %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/calibre-viewer.svg

# don't put bash completions in /usr/etc
mv %{buildroot}%{_prefix}%{_sysconfdir} %{buildroot}

# these are provided as separate packages
rm -rf %{buildroot}%{_libdir}/%{name}/{odf,cherrypy,pyPdf,encutils,cssutils}
rm -rf %{buildroot}%{_libdir}/%{name}/cal/utils/genshi
rm -rf %{buildroot}%{_libdir}/%{name}/cal/trac

# link to system fonts after we have deleted (see Source0) the non-free ones
# http://bugs.calibre-ebook.com/ticket/3832
ln -s %{_datadir}/fonts/liberation/LiberationSans-Regular.ttf \
      %{buildroot}%{_datadir}/%{name}/fonts/prs500/tt0003m_.ttf
ln -s %{_datadir}/fonts/liberation/LiberationSerif-Regular.ttf \
      %{buildroot}%{_datadir}/%{name}/fonts/prs500/tt0011m_.ttf
ln -s %{_datadir}/fonts/liberation/LiberationMono-Regular.ttf \
      %{buildroot}%{_datadir}/%{name}/fonts/prs500/tt0419m_.ttf

# http://bugs.calibre-ebook.com/ticket/3770#comment:7
# man pages
mv %{buildroot}%{_datadir}/%{name}/man %{buildroot}%{_mandir}

# move locales
mv %{buildroot}%{_datadir}/%{name}/localization/locales \
   %{buildroot}%{_datadir}/locale
for file in %{buildroot}%{_datadir}/locale/*/LC_MESSAGES/messages.mo; do
    lang=$(echo $file|%{__sed} 's:.*locale/\(.*\)/LC_MESSAGES.*:\1:')
    mv %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/messages.mo \
       %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/%{name}.mo
done;
for file in %{buildroot}%{_datadir}/locale/*/LC_MESSAGES/iso639.mo; do
    lang=$(echo $file|%{__sed} 's:.*locale/\(.*\)/LC_MESSAGES.*:\1:')
    mv %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/iso639.mo \
       %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/%{name}_iso639.mo
done;
for file in %{buildroot}%{_datadir}/locale/*/LC_MESSAGES/qt.qm; do
    lang=$(echo $file|%{__sed} 's:.*locale/\(.*\)/LC_MESSAGES.*:\1:')
    mv $file %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/%{name}_$lang.qm
done;

%find_lang %{name} --with-qt --all-name

# locales should be looked for in the proper place
%{__sed} -i -e "s:P('localization/locales:('/usr/share/locale:" \
            -e "s/messages.mo/calibre.mo/"                   \
            -e "s/iso639.mo/calibre_iso639.mo/"              \
            %{buildroot}%{_libdir}/%{name}/%{name}/utils/localization.py

%{__rm} -f %{buildroot}%{_bindir}/%{name}-uninstall   

%clean
%{__rm} -rf %{buildroot}

%post
update-desktop-database &> /dev/null ||:
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ] ; then
%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
update-desktop-database &> /dev/null ||:
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ] ; then
%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc COPYRIGHT LICENSE Changelog.yaml

%{_bindir}/*
%config(noreplace) %{_sysconfdir}/bash_completion.d/
%{_libdir}/%{name}
%{_prefix}/lib/udev/rules.d/*
%{_datadir}/%{name}
%{_datadir}/pixmaps/*
%{_datadir}/applications/*
%{_datadir}/mime/packages/*
%{_datadir}/icons/hicolor/scalable/mimetypes/*
%{_datadir}/icons/hicolor/scalable/apps/*
%{_mandir}/man1/*

%changelog
* Fri Feb 26 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.42-1
- new upstream release 0.6.42
- remove shebang from default_tweaks.py

* Mon Feb  1 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.37-1
- new upstream release 0.6.37

* Fri Jan 29 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.36-1
- new upstream release 0.6.36
- fixed a cssprofiles issue with loading the profiles

* Tue Jan 26 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.35-3
- added -cssprofiles patch to cvs 

* Tue Jan 26 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.35-2
- remove python-cssutils 0.9.6 dependency

* Mon Jan 25 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.35-1
- new upstream release
- fedora includes cssutils >= 0.9.6 now; removed the cssprofiles patch
- removed -executables patch, upstream fixed it: http://bugs.calibre-ebook.com/ticket/4437

* Wed Jan  6 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.32-2
- fix for package tagged without adding new patch to cvs

* Wed Jan  6 2010 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.32-1
- new upstream release 0.6.32
- project website has changed
- added python-BeautifulSoup BuildRequire
- new patch to fix full buildpath in binary files

* Sun Dec  6 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.26-1
- New upstream version
- Regenerated no-update patch because of code relocation

* Wed Dec  2 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.25-1
- New upstream release

* Wed Nov 18 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.24-1
- New upstream release: http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.2416Nov2009

* Mon Nov 16 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.23-1
- new upstream release: http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.2313Nov2009
- patch to stop checking for new upstream version

* Sat Nov  7 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.21-1
- new upstream version: http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.2106Nov2009
- added python-BeautifulSoup requirement

* Wed Nov  4 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> - 0.6.20-1
- new upstream version:
http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.2030Oct2009
- upstream now ships correct .desktop files
- fixed missing dependency: PyQt4
- fixed calibre-gui icon

* Thu Oct 22 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.19-3
- removed unfree fonts from source package

* Thu Oct 22 2009 Ionuț C. Arțăriși <mapleoin@fedoraproject.org> - 0.6.19-2
- readability enhancements
- added python-genshi requires
- removed libwmf require since ImageMagick provides libwmf-lite as a
  dependency and that's what we actually need

* Wed Oct 21 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> - 0.6.19-1
- new upstream version:
  http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.1920Oct2009
- delete fonts, calibre can find the system fonts
- specify libdir as an install option, so calibre will link properly
  even on 64bit

* Mon Oct 19 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> - 0.6.18-1
- updated requires list
- new upstream release
- can override CFLAGS now
- removed trac and genshi duplicates
- use xdg env variables to do desktop integration in the buildroot
- added xdg-utils buildrequire
- install udev rules in /usr/lib even on 64bit and don't own the whole dir
- removed wrongly used Version field from .desktop files

* Mon Oct 12 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> - 0.6.17-2
- mimick what calibre's desktop-integration script does (mimetypes, icons etc.)
- removed unneeded INSTALL file
- marked bash completion file as config(noreplace) and take ownership of the dir

* Sat Oct 10 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> - 0.6.17-1
- new upstream release: http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.1709Oct2009
- the install process changed significantly
- locales were added

* Thu Sep 10 2009 Ionuț Arțăriși <mapleoin@lavabit.com> - 0.6.11-1
- new upstream release: http://calibre.kovidgoyal.net/wiki/Changelog#Version0.6.1104Sep2009
- minor path fixes
- rearranged files section

* Fri Aug 28 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> 0.6.10-1
- handle desktop files
- don't compress manpages and don't list them as duplicates
- added lrfviewer icon

* Tue Aug 25 2009 Ionuț Arțăriși <mapleoin@fedoraproject.org> 0.6.8-1
- Initial RPM release
