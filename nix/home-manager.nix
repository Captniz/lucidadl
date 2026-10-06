{ config, lib, pkgs, ... }:

let
  cfg = config.programs.lucidadl;
in
{
  options.programs.lucidadl = {
    enable = lib.mkEnableOption "lucidadl";

    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.lucidadl;
      defaultText = lib.literalExpression "pkgs.lucidadl";
      description = "The lucidadl package to install.";
    };
  };

  config = lib.mkIf cfg.enable {
    home.packages = [ cfg.package ];
  };
}