{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable/";
    poetry2nix.url = "github:nix-community/poetry2nix";
    devenv.url = "github:cachix/devenv";
  };

  outputs = inputs @ {
    nixpkgs,
    flake-parts,
    poetry2nix,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = nixpkgs.lib.systems.flakeExposed;
      imports = [inputs.devenv.flakeModule];
      perSystem = {
        pkgs,
        lib,
        ...
      }: let
        inherit (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication;
        inherit (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) defaultPoetryOverrides;
        app = mkPoetryApplication {
          projectDir = lib.cleanSource ./.;
          preferWheels = true;
          overrides =
            defaultPoetryOverrides.extend
            (_self: super: {
              secure-smtplib =
                super.secure-smtplib.overridePythonAttrs
                (
                  old: {
                    buildInputs = (old.buildInputs or []) ++ [super.setuptools];
                  }
                );
            });
        };
        script = pkgs.writeShellScriptBin "run.sh" ''
          ${app.dependencyEnv}/bin/gunicorn --worker-class uvicorn.workers.UvicornWorker --workers $(nproc) "$@" app.main:app
        '';
      in {
        packages.default = app;
        apps.default = {
          type = "app";
          program = script;
        };
        devenv.shells.default = {
          containers = lib.mkForce {};
          packages = [
            pkgs.poetry
          ];
        };
      };
    };
}
