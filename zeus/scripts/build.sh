bin_file="${build_dir}/${bin_name}"
find src/chopper src/chopper/providers \
        -maxdepth 1 -type f -name \*.py \
    | sort -u | while read src_file; do
    (cat "${src_file}"; echo) >> "${bin_file}"
done
cat src/main.py >> "${bin_file}"
sed -i '/^from\ \./d; /^from\ chopper/d; /^$/d; /^#/d' "${bin_file}"
mv -f "${bin_file}"{,.old}
(echo '#!/usr/bin/python3'; cat "${bin_file}.old") > "${bin_file}"
rm -f "${bin_file}.old"
chmod a+x "${bin_file}"