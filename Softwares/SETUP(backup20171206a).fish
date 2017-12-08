#!/usr/bin/fish
# 
# CURRENT DIR
set -gx ALMACOSMOS (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status --current-filename)))
if [ x"$ALMACOSMOS" = x"" ]
    echo "Failed to source "(status --current-filename)"!"; exit
end
#
# PATH
if not contains "$ALMACOSMOS" $PATH
    set -gx PATH "$ALMACOSMOS" $PATH
end
if not contains "$ALMACOSMOS/3rd/bin" $PATH
    set -gx PATH "$ALMACOSMOS/3rd/bin" $PATH
end
#
# LIST
set -x ALMACOSMOSCMD "almacosmos-sky-coverage" "almacosmos-fits-image-to-coverage-polyogn" "almacosmos-analyze-fits-image-pixel-histogram" "caap-generate-PSF-Gaussian-2D" "almacosmos-highz-galaxy-crossmatcher" "almacosmos-highz-galaxy-crossmatcher-read-results"
# 
# CHECK
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
if status --is-interactive
  for TEMPTOOLKITCMD in {$ALMACOSMOSCMD}
    type $TEMPTOOLKITCMD
  end
end


