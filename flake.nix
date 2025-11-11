{
  outputs =
    { self, nixpkgs, ... }@inputs:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
    {
      formatter.x86_64-linux = pkgs.nixfmt-rfc-style;
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = with pkgs; [
          python310
          zlib
        ];
        LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib.out}/lib";
        shellHook = ''
          echo "Python 3.10 dev shell"
        '';
      };

    };
}
