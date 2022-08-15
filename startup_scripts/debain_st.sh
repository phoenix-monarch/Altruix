# !/bin/bash

_isInstalled() {
    package="$1";
    if [ $(dpkg-query -W -f='${Status}' $1 2>/dev/null | grep -c "ok installed") ];
    then
        echo 0; 
        return;
    fi;
        echo 1;
        return
}

_installMany() {
    toInstall=();
    for pkg; do
        if [[ $(_isInstalled "${pkg}") == 0 ]]; then
            echo "${pkg} is already installed.";
            continue;
        fi;
        toInstall+=("${pkg}");
    done;
    if [[ "${toInstall[@]}" == "" ]] ; then
        echo "All packages are already installed.";
        return;
    fi;
    printf "Packages not installed:\n%s\n" "${toInstall[@]}";
    sudo apt install "${toInstall[@]}";
}


final_run () {
    _installMany python3 ffmpeg python3-pip # install these debain packages
    python3 -m venv venv
    source venv/bin/activate
    pip3 install --upgrade pip && pip3 install -r requirements.txt
    python3 -m Main
}


final_run