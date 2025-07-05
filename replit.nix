{ pkgs }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python311Full
    pkgs.cacert
    pkgs.gcc
  ];
}