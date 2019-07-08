#!/bin/bash
# 

echo "source almacosmos_cmd_args -aaa 1 -aaa 2 -bbb --ccc 100 -ccc"
source almacosmos_cmd_args -aaa 1 -aaa 2 -bbb --ccc 100 -ccc

echo "almacosmos_cmd_main_args = ${almacosmos_cmd_main_args[@]} (${#almacosmos_cmd_main_args[@]})"
echo "almacosmos_cmd_main_opts = ${almacosmos_cmd_main_opts[@]} (${#almacosmos_cmd_main_opts[@]})"
echo "almacosmos_cmd_misc_args = ${almacosmos_cmd_misc_args[@]} (${#almacosmos_cmd_misc_args[@]})"
echo "almacosmos_cmd_misc_opts = ${almacosmos_cmd_misc_opts[@]} (${#almacosmos_cmd_misc_opts[@]})"
echo "almacosmos_cmd_aaa = ${almacosmos_cmd_aaa[@]} (${#almacosmos_cmd_aaa[@]})"
echo "almacosmos_cmd_bbb = ${almacosmos_cmd_bbb[@]} (${#almacosmos_cmd_bbb[@]})"
echo "almacosmos_cmd_ccc = ${almacosmos_cmd_ccc[@]} (${#almacosmos_cmd_ccc[@]})"

if [[ -z "${almacosmos_cmd_bbb}" ]]; then
    echo "almacosmos_cmd_bbb is -z. ${#almacosmos_cmd_bbb[@]}"
fi

if [[ -z "${almacosmos_cmd_ddd}" ]]; then
    echo "almacosmos_cmd_ddd is -z. ${#almacosmos_cmd_ddd[@]}"
fi