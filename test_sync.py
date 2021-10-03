import tempfile
from pathlib import Path
import shutil
from sync import sync, determine_actions


# 이 테스트들은 도메인 로직이 File I/O 로직과 너무 긴밀히 결합되어 있다!

# E2E : End To End
class TestE2E:
    # 인스턴스 없이도 Class 내부 메서드를 실행할 수 있다.
    @staticmethod
    # 원본(Source) 에는 있는데, 사본(Dest) 에는 없는 파일 => 복사되어야 한다.
    def test_when_a_file_exists_in_the_source_but_not_the_destination():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a very useful file"
            (Path(source) / "my-file").write_text(content)

            sync(source, dest)

            expected_path = Path(dest) / "my-file"
            assert expected_path.exists()
            assert expected_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

    @staticmethod
    # Source에서 이름이 바뀐 파일, => Dest에서 이름이 바뀌어야 한다.
    # 즉, 파일내용 같은데 이름이 다른 파일은 이름이 동기화되어야 한다.
    def test_when_a_file_has_been_renamed_in_the_source():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a file that was renamed"
            source_path = Path(source) / "source-filename"
            old_dest_path = Path(dest) / "dest-filename"
            expected_dest_path = Path(dest) / "source-filename"
            source_path.write_text(content)
            old_dest_path.write_text(content)

            sync(source, dest)

            assert old_dest_path.exists() is False
            assert expected_dest_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

# 추상화 적용
# 동기화할때, 세 방법 중 하나를 선택해야 한다.
# 1. 원본에는 파일이 있지만, 사본에 없으면 파일을 원본 -> 사본 복사
# 2. 원본에 파일이 있지만, 사본에 있는 (내용이 같은) 파일과 이름이 다르면, 사본의 파일 이름을 원본 파일 이름과 같게 변경
# 3. 사본에 파일이 있지만, 원본에는 없다면 사본의 파일을 삭제
# 이를  1 : ("COPY", "sourcePath", "DestPath") , 2 : ("MOVE", "old", "new") 식으로 추상화한다. 


# 1. 의 경우
def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {}
    actions = determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dst"))
    assert list(actions) == [("COPY", Path("/src/fn1"), Path("/dst/fn1"))]

# 2.의 경우
def test_when_a_file_has_been_renamed_in_the_source():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {"hash1": "fn2"}
    actions = determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dst"))
    assert list(actions) == [("MOVE", Path("/dst/fn2"), Path("/dst/fn1"))]
