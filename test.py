from ansys.aedt.core import Desktop, Maxwell3d

# Maxwell Desktop 실행
desktop = Desktop(
    version=None,          # 자동 감지
    new_desktop=True,      # 새 세션
    non_graphical=False,   # GUI 실행
    close_on_exit=False
)

m3d = Maxwell3d() # Maxwell3D 객체 연결

# 단순 모델 생성
m3d.modeler.model_units = "mm"
m3d.modeler.create_box([0,0,0], [10,10,10], name="Box1")
m3d.create_setup(name="Setup1")
m3d.analyze_setup("Setup1")

# 종료
# m3d.release_desktop(close_projects=True, close_desktop=True)
