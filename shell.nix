{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    pdm
    ruff
    # required for taplo-pre-commit
    cargo
    # required for pytest-docker
    docker-compose
  ];

  shellHook = ''
    # dirty hack to get ruff-pre-commit working
    ruff_bin=$(find ~/.cache/pre-commit -type f -name ruff)
    [ -f "$ruff_bin" ] && ln -sf ${pkgs.ruff}/bin/ruff $ruff_bin

    # dirty hack to get ruff in venv working
    ruff_bin=$(find .venv -type f -name ruff)
    [ -f "$ruff_bin" ] && ln -sf ${pkgs.ruff}/bin/ruff $ruff_bin
  '';
}
