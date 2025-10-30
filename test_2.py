from ansys.aedt.core import Maxwell2d
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_dir, "Solenoid.aedt")

# Maxwell2d로 열기
try:
    m2d = Maxwell2d(
        project=project_path,
        design="Solenoid",
        close_on_exit=False,
    )
    print("=" * 60)
    print("✓ 프로젝트 연결 성공")
    print(f"  프로젝트: {m2d.project_name}")
    print(f"  디자인: {m2d.design_name}")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ 프로젝트 연결 실패: {e}")
    exit()

# 변수 확인
print("\n[1단계] 현재 변수 확인:")
for var_name in ["deltagap", "curr"]:
    try:
        val = m2d[var_name]
        print(f"  ✓ {var_name} = {val}")
    except Exception as e:
        print(f"  ✗ {var_name}: 접근 불가 - {e}")

# 변수 값 설정
print("\n[2단계] 시뮬레이션 매개변수 설정:")
deltagap_values = ["0in", "0.05in", "0.1in", "0.15in", "0.2in", "0.25in", "0.3in", "0.35in", "0.4in", "0.45in", "0.5in"]
current_values = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1500]
print(f"  Gap values: {deltagap_values}")
print(f"  Current values: {current_values} (×100 A)")

results = []
total_sims = len(deltagap_values) * len(current_values)
sim_count = 0

# 변수별 반복 시뮬레이션
print(f"\n[3단계] 시뮬레이션 및 분석 실행 ({total_sims}개):")

for gap in deltagap_values:
    for curr_idx, curr_val in enumerate(current_values):
        sim_count += 1
        curr_amp = curr_val * 100  # 100A 단위로 변환
        
        print(f"\n  [{sim_count}/{total_sims}] deltagap={gap}, curr={curr_amp}A")
        
        try:
            # 변수 설정
            m2d["deltagap"] = gap
            m2d["curr"] = f"{curr_amp}A"
            print(f"      ✓ 변수 설정 완료")
            
            # 해석 실행
            m2d.analyze_setup("Setup1")
            print(f"      ✓ 해석 실행 완료")
            
            # 결과 추출 - Force 값 가져오기
            try:
                # Maxwell의 출력 변수에서 Force 값 추출
                force_value = m2d.post.get_solution_data(
                    expressions=["Force1.Force_z"],
                    setup_sweep_name="Setup1"
                )
                
                # 데이터 추출
                if force_value is not None:
                    force_z = force_value.data_real("Force1.Force_z")
                    if force_z is not None and len(force_z) > 0:
                        force_result = force_z[0]  # 첫 번째 값 추출
                    else:
                        force_result = None
                else:
                    force_result = None
                
                print(f"      Force_z = {force_result} N")
                
                results.append({
                    "deltagap": gap,
                    "curr": curr_amp,
                    "Force_z": force_result
                })
                
            except Exception as force_e:
                print(f"      ⚠ Force 값 추출 실패: {force_e}")
                results.append({
                    "deltagap": gap,
                    "curr": curr_amp,
                    "Force_z": None
                })
            
        except Exception as e:
            print(f"      ✗ 오류: {e}")
            results.append({
                "deltagap": gap,
                "curr": curr_amp,
                "Force_z": None
            })

# 결과 요약
print("\n" + "=" * 60)
print("[4단계] 시뮬레이션 결과 요약:")
print("=" * 60)
print(f"  총 시뮬레이션: {total_sims}개")
completed = sum(1 for r in results if r["Force_z"] is not None)
failed = total_sims - completed
print(f"  성공: {completed}개, 실패: {failed}개")

if results:
    print("\n  처음 5개 결과:")
    for i, r in enumerate(results[:5], 1):
        print(f"    {i}. deltagap={r['deltagap']}, curr={r['curr']}A, Force_z={r['Force_z']} N")

# 프로젝트 저장
print("\n[5단계] 프로젝트 저장:")
try:
    m2d.save_project()
    print("  ✓ 프로젝트 저장 완료")
except Exception as e:
    print(f"  ✗ 저장 실패: {e}")

# CSV로 저장
print("\n[6단계] 결과를 CSV 파일로 저장:")
try:
    import pandas as pd
    
    # DataFrame 생성
    df = pd.DataFrame(results)
    
    # CSV 파일명 생성
    csv_filename = os.path.join(current_dir, f"Force_vs_Gap_Current_{int(time.time())}.csv")
    
    # CSV 저장
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    
    print(f"  ✓ CSV 저장 완료")
    print(f"    파일명: {os.path.basename(csv_filename)}")
    print(f"    저장 위치: {current_dir}")
    print(f"    데이터 행 수: {len(df)}")
    print(f"\n  CSV 파일 내용 미리보기:")
    print(df.head(10).to_string(index=False))
    
except ImportError:
    print("  ⚠ pandas 모듈이 없습니다. 설치 후 다시 시도하세요:")
    print("    pip install pandas")
except Exception as e:
    print(f"  ✗ CSV 저장 실패: {e}")

# 파일 확인
print("\n[7단계] 생성된 파일 확인:")
try:
    csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
    if csv_files:
        print(f"  ✓ 생성된 CSV 파일:")
        for csv_f in sorted(csv_files, reverse=True)[:3]:  # 최근 3개만 표시
            file_path = os.path.join(current_dir, csv_f)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"    - {csv_f} ({file_size:.2f} KB)")
    else:
        print(f"  ⚠ CSV 파일을 찾을 수 없습니다")
except Exception as e:
    print(f"  ✗ 파일 확인 실패: {e}")

# 세션 종료
print("\n[8단계] 세션 종료:")
try:
    m2d.release_desktop(close_projects=True, close_desktop=True)
    print("  ✓ Maxwell 세션 종료 완료")
except Exception as e:
    print(f"  ✗ 종료 중 오류: {e}")

print("\n" + "=" * 60)
print("모든 작업 완료!")
print("=" * 60)