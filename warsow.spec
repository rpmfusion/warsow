%global warsow_libdir %{_prefix}/lib/warsow
%global warsow_datadir %{_datadir}/warsow

Name:           warsow
Version:        1.02
Release:        2%{?dist}
Summary:        Fast paced 3D first person shooter

License:        GPLv2+
URL:            http://www.warsow.net/
Source0:        http://www.warsow.net:1337/~warsow/%{version}/warsow_%{version}_sdk.tar.gz
Source1:        warsow.desktop
Source2:        warsow48x48.png
Source3:        warsow.svg
# Downstream patch to set the locations of the data files and libs
Patch0:         warsow-paths.patch
# Downstream patch to stop stripping the binaries and to avoid linking with
# the static c++ runtime
Patch1:         warsow-build.patch

BuildRequires:  curl-devel
BuildRequires:  desktop-file-utils
BuildRequires:  freetype-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libtheora-devel
BuildRequires:  libvorbis-devel
BuildRequires:  libX11-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXxf86dga-devel
BuildRequires:  libXxf86vm-devel
BuildRequires:  openal-devel
BuildRequires:  openssl-devel
BuildRequires:  SDL-devel
Requires:       hicolor-icon-theme
Requires:       warsow-data = %{version}

%description
Warsow is a fast paced first person shooter consisting of cel-shaded
cartoon-like graphics with dark, flashy and dirty textures. Warsow is based on
the E-novel "Chasseur de bots" ("Bots hunter" in English) by Fabrice Demurger.
Warsow's codebase is built upon Qfusion, an advanced modification of the Quake
II engine.

This package installs the client to play Warsow.


%package server
Summary:        Dedicated server for Warsow
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-data = %{version}

%description server
Warsow is a fast paced first person shooter consisting of cel-shaded
cartoon-like graphics with dark, flashy and dirty textures. Warsow is based on
the E-novel "Chasseur de bots" ("Bots hunter" in English) by Fabrice Demurger.
Warsow's codebase is built upon Qfusion, an advanced modification of the Quake
II engine.

This package installs the standalone server and TV server for Warsow.


%prep
%setup -q -n warsow_%{version}_sdk
%patch0 -p1 -b .paths
%patch1 -p1 -b .build

# Remove bundled libs
pushd libsrcs
rm -rf libcurl libfreetype libjpeg libogg libpng libtheora libvorbis zlib
popd

# Convert to utf-8 and Unix line breaks
for file in docs/license.txt; do
    iconv -f WINDOWS-1252 -t UTF-8 -o $file.new $file &&
    sed -i 's/\r//' $file.new &&
    touch -r $file $file.new &&
    mv $file.new $file
done


%build
pushd source
export CFLAGS="%optflags"
export LDFLAGS="%__global_ldflags"
make \
    BUILD_CLIENT=YES \
    BUILD_SERVER=YES \
    BUILD_TV_SERVER=YES \
    BUILD_IRC=YES \
    BUILD_SND_OPENAL=YES \
    BUILD_SND_QF=YES \
    DEBUG_BUILD=NO
popd


%install
pushd source/release
# Install the executables directly to bindir. We are setting the data paths
# correctly with patch0, so we have no need for the shell script wrappers.
install -Dm 755 warsow.* $RPM_BUILD_ROOT%{_bindir}/warsow
install -Dm 755 wsw_server.* $RPM_BUILD_ROOT%{_bindir}/warsow-server
install -Dm 755 wswtv_server.* $RPM_BUILD_ROOT%{_bindir}/warsow-tv-server

# Install the private libraries to a private directory
install -d $RPM_BUILD_ROOT%{warsow_libdir}/libs
install -m 755 libs/*.so $RPM_BUILD_ROOT%{warsow_libdir}/libs/
popd

# Install icons and the desktop file
install -D -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/48x48/apps/warsow.png
install -D -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps/warsow.svg
desktop-file-install %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/applications/warsow.desktop


%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%doc docs/license.txt
%{_bindir}/warsow
%{_datadir}/icons/hicolor/*/apps/warsow.png
%{_datadir}/icons/hicolor/scalable/apps/warsow.svg
%{_datadir}/applications/warsow.desktop
%{warsow_libdir}/

%files server
%{_bindir}/warsow-server
%{_bindir}/warsow-tv-server

%changelog
* Mon May 06 2013 Kalev Lember <kalevlember@gmail.com> - 1.02-2
- Review fixes (https://bugzilla.rpmfusion.org/show_bug.cgi?id=2762):
- Require hicolor-icon-theme
- Convert license.txt to Unix line breaks
- Don't distribute docs that describe source code
- server: Depend on the main package

* Mon Apr 15 2013 Kalev Lember <kalevlember@gmail.com> - 1.02-1
- Initial Fedora package
