{ pkgs }:
pkgs.mkShell {
  buildInputs = [
    pkgs.cacert
    pkgs.gcc
  ];
}