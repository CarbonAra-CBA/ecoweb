import os
import subprocess
import shutil
from pathlib import Path
import json
import sys

# Gulpfile.js 내용을 문자열로 정의
GULPFILE_CONTENT = """import gulp from 'gulp';
import terser from 'gulp-terser';
import cleanCSS from 'gulp-clean-css';
import path from 'path';

// JavaScript 파일 최적화
function optimizeJS() {
  console.log('🛠 JS 최적화 시작 경로:', path.resolve(process.cwd()));
  return gulp.src(['**/*.js', '!node_modules/**'], { base: './' })
    .pipe(terser({
      compress: {
        drop_console: true,
        drop_debugger: true,
        ecma: 2023,
      },
      output: {
        comments: false,
        ecma: 2023,
      }
    }))
    .pipe(gulp.dest('./')); // 원본 파일에 덮어쓰기
}

// CSS 파일 최적화
function optimizeCSS() {
  console.log('🔍 CSS 최적화 시작 경로:', path.resolve(process.cwd()));
  return gulp.src('**/*.css', { base: './' })
    .pipe(cleanCSS({
      compatibility: 'ie8',
      level: {
        1: {
          specialComments: 0,
          removeEmpty: true,
          removeWhitespace: true
        },
        2: {
          mergeMedia: true,
          removeEmpty: true,
          removeDuplicateFontRules: true,
          removeDuplicateMediaBlocks: true,
          removeDuplicateRules: true,
          removeUnusedAtRules: true
        }
      }
    }))
    .pipe(gulp.dest('./')); // 원본 파일에 덮어쓰기
}

// 기본 태스크 수정
const build = gulp.series(
  () => Promise.resolve('Starting build...').then(console.log),
  gulp.parallel(optimizeCSS, optimizeJS) // optimizeImages 추가
);

export default build;
"""

def check_npm_installed(env):
    """npm이 설치되어 있는지 확인합니다."""
    try:
        result = subprocess.run(['npm', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True, shell=True, env=env)
        print(f"✅ npm 버전: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def optimize_project(project_path: Path):
    """
    주어진 프로젝트 폴더에서 최적화 작업을 수행합니다.
    
    Args:
    - project_path (Path): 웹 프로젝트 폴더 경로
    """
    
    project_path = Path(project_path).resolve()
    print(f"🔧 최적화 시작: {project_path}")

    # 현재 환경 변수 복사 및 PATH 추가 확인
    env = os.environ.copy()

    # npm 설치 확인
    if not check_npm_installed(env):
        print("❌ npm이 설치되어 있지 않습니다. npm을 먼저 설치해주세요.")
        print("💡 Node.js를 설치하면 npm도 함께 설치됩니다: https://nodejs.org/")
        return

    # Step 1: npm init -y
    try:
        print("📦 npm init -y 실행 중...")
        subprocess.run(['npm', 'init', '-y'], cwd=project_path, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ npm init -y 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ npm init 에러: {e.stderr.decode().strip()}")
        return

    # Step 2: npm install --save-dev gulp gulp-uglify gulp-clean-css gulp-imagemin gulp-terser
    try:
        print("📦 npm install --save-dev gulp gulp-uglify gulp-clean-css gulp-terser 실행 중...")
        subprocess.run(['npm', 'install', '--save-dev', 'gulp', 'gulp-uglify', 'gulp-clean-css', 'gulp-terser'], cwd=project_path, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ npm install --save-dev 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ npm install 에러: {e.stderr.decode().strip()}")
        return

    # Step 3: Write gulpfile.mjs
    try:
        print("📝 gulpfile.mjs 작성 중...")
        gulpfile_path = project_path / 'gulpfile.mjs'
        with open(gulpfile_path, 'w', encoding='utf-8') as f:
            f.write(GULPFILE_CONTENT)
        print("✅ gulpfile.mjs 작성 완료")
    except Exception as e:
        print(f"❌ gulpfile.mjs 작성 에러: {e}")
        return

    # Step 3.1: Modify package.json to include "type": "module"
    try:
        print("🔧 package.json 수정 중...")
        package_json_path = project_path / 'package.json'
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_json = json.load(f)
        
        package_json['type'] = 'module'
        
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        print("✅ package.json 수정 완료")
    except Exception as e:
        print(f"❌ package.json 수정 에러: {e}")
        return

    # Step 4: Run gulp
    try:
        print("🚀 gulp 실행 중...")
        # Use npx to run local gulp
        subprocess.run(['gulp'], cwd=project_path, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ gulp 실행 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ gulp 실행 에러: {e.stderr.decode().strip()}")
        return

    # Step 5: Delete node_modules, package-lock.json, package.json, gulpfile.mjs
    try:
        print("🗑️ 불필요한 파일 및 폴더 삭제 중...")
        node_modules_path = project_path / 'node_modules'
        package_lock_path = project_path / 'package-lock.json'
        package_json_path = project_path / 'package.json'
        gulpfile_path = project_path / 'gulpfile.mjs'

        if node_modules_path.exists():
            shutil.rmtree(node_modules_path)
            print("✅ node_modules 삭제 완료")
        else:
            print("⚠️ node_modules 폴더가 존재하지 않습니다.")

        if package_lock_path.exists():
            package_lock_path.unlink()
            print("✅ package-lock.json 삭제 완료")
        else:
            print("⚠️ package-lock.json 파일이 존재하지 않습니다.")

        if package_json_path.exists():
            package_json_path.unlink()
            print("✅ package.json 삭제 완료")
        else:
            print("⚠️ package.json 파일이 존재하지 않습니다.")

        if gulpfile_path.exists():
            gulpfile_path.unlink()
            print("✅ gulpfile.mjs 삭제 완료")
        else:
            print("⚠️ gulpfile.mjs 파일이 존재하지 않습니다.")
    except Exception as e:
        print(f"❌ 파일 삭제 에러: {e}")
        return

    # Step 6: Zip the optimized project folder
    try:
        print("📦 프로젝트 폴더 압축 중...")
        zip_filename = project_path.with_suffix('.zip').name
        zip_path = project_path.parent / f"{project_path.name}.zip"
        # Create zip archive
        shutil.make_archive(base_name=project_path.parent / project_path.name, format='zip', root_dir=project_path)
        print(f"✅ 프로젝트 압축 완료: {zip_path}")
    except Exception as e:
        print(f"❌ 프로젝트 압축 에러: {e}")
        return None

    print(f"🎉 최적화 완료: {project_path.name}\n")
    return zip_path

def code_optimizer(root_path):
    # 절대 경로로 변환
    webprojects_path = Path(root_path).resolve()
    if not webprojects_path.exists():
        print(f"❌ webprojects 경로가 존재하지 않습니다: {webprojects_path}")
        sys.exit(1)

    # 경로가 존재하는지 한번 더 확인
    print(f"📂 작업 경로 확인: {webprojects_path}")
    if not webprojects_path.is_dir():
        print("❌ 유효한 디렉토리가 아닙니다.")
        sys.exit(1)

    return optimize_project(webprojects_path)

def getCodeSize_before(root_path):
    result = {}
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.js') or file.endswith('.css'):
                file_path = os.path.join(root, file)
                size_bytes = os.path.getsize(file_path)
                size_kb = size_bytes / 1024  # Convert bytes to KB
                relative_path = os.path.relpath(file_path, root_path)
                result[relative_path] = {'beforeSize': size_kb}
    return result

def getCodeSize_after(root_path, result):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.js') or file.endswith('.css'):
                file_path = os.path.join(root, file)
                size_bytes = os.path.getsize(file_path)
                size_kb = size_bytes / 1024  # Convert bytes to KB
                relative_path = os.path.relpath(file_path, root_path)
                if relative_path in result:
                    result[relative_path]['afterSize'] = size_kb
                else:
                    result[relative_path] = {'afterSize': size_kb}
    return result
    

if __name__ == "__main__":
    code_optimizer("./ecoweb/app/static/webprojects/www.airkorea.or.kr")
