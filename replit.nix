# replit.nix  ── 최소 예시
{ pkgs }:

{
  deps = [
    pkgs.python311Full           # 사용 중인 파이썬 버전
    pkgs.openjdk17_headless      # ↔ openjdk11_headless 도 OK
    pkgs.gcc                     # 일부 파이썬 패키지 컴파일용
  ];
}
