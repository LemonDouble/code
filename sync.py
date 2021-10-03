import hashlib
import os
import shutil
from pathlib import Path


# 파일 디렉터리 동기화
# 1. 원본에는 파일이 있지만, 사본에 없으면 파일을 원본 -> 사본 복사
# 2. 원본에 파일이 있지만, 사본에 있는 (내용이 같은) 파일과 이름이 다르면, 사본의 파일 이름을 원본 파일 이름과 같게 변경
# 3. 사본에 파일이 있지만, 원본에는 없다면 사본의 파일을 삭제


# Source 와 Dest는 디렉토리, Dest = 사본
def sync(source, dest):
    # Soruce, Dest 디렉토리 돌며, 
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # ("COPY", "sourcePath", "DestPath").. 처럼 추상화한 결과 반환
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # actions의 각각의 결과에 대해, 해당 액션을 실행
    
    # 근데 *paths는 뭐지..
    # shutil에 들어가는 파라미터, actions를 봤을 때 sorucePath, DestPath를 묶은 값인 것 같다.
    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(*paths)
        if action == "MOVE":
            shutil.move(*paths)
        if action == "DELETE":
            os.remove(paths[0])


# 요구사항 2. 를 위해 Hash를 사용한다.
# (파일이 수정되었음을 감지하기 위해 파일을 hash한 값이 같은지 확인하는 로직이 필요!)
BLOCKSIZE = 65536

# 파일을 block size만큼 읽어 Hash한 후, 결과를 반환하는 함수
def hash_file(path):
    # SHA-1 : 임의 길이의 입력 데이터를, 160bit의 출력 데이터로 바꾼다.
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_paths_and_hashes(root):
    # 원본 폴더의 자식들을 순회하며, 파일 이름과 해시의 사전을 만든다.
    hashes = {}
    # os.walk : 하위 폴더를 쉽게 검색할 수 있도록 해 주는 함수
    # parameter의 하위 폴더 각각에 대해 folder, dirs, files 반환하는데,
    # folder : 현재 작업중인 디렉토리
    # dirs : 현재 작업중인 디렉토리에 있는 디렉토리
    # files : 현재 작업중인 디렉토리에 있는 파일들
    for folder, _, files in os.walk(root):
        for fn in files:
            # KEY : HASH 결과값, Value : 파일 이름인 딕셔너리 만든다.
            # 아마 KEY를 Hash 결과값으로 쓴 건, 같은 파일이름 있을 가능성 높아서 뒤집은 것 같다.
            # hash_file(Path(folder) / fn) 는 나누기 연산 아니다!
            # data = Path("/home/temp") / "hello" 하면 "/home/temp/hello" 나온다. 즉, File의 Full path이다.
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes


def determine_actions(source_hashes, dest_hashes, source_folder, dest_folder):
    # .items()로 딕셔너리를 [(sha1, filename1), (sha2,filename2) ... ] 식으로 바꾼 후
    # 각각을 sha, filename이라는 변수로 받아 foreach 돌린다.

    for sha, filename in source_hashes.items():
        # 1. 원본에는 파일이 있지만, 사본에 없으면 파일을 원본 -> 사본 복사
        if sha not in dest_hashes:
            sourcepath = Path(source_folder) / filename
            destpath = Path(dest_folder) / filename
            # 또 yield... 단순히 이런 식으로 변수 세개 yield하면 Tuple로 반환되는건가?
            yield "COPY", sourcepath, destpath

        # 2. 원본에 파일이 있지만, 사본에 있는 (내용이 같은) 파일과 이름이 다르면, 사본의 파일 이름을 원본 파일 이름과 같게 변경
        elif dest_hashes[sha] != filename:
            olddestpath = Path(dest_folder) / dest_hashes[sha]
            newdestpath = Path(dest_folder) / filename
            yield "MOVE", olddestpath, newdestpath

    # 3. 사본에 파일이 있지만, 원본에는 없다면 사본의 파일을 삭제
    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield "DELETE", dest_folder / filename
