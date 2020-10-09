from index import Index
import pytest 

def test_missing_index_file():
    with pytest.raises(FileNotFoundError):
        db = Index("bad/path/to/bogus/file")
        db.load()

def test_valid_index_file():
    db = Index("test/data/NutritionFactswithDrGreger/idx/061020.idx")
    db.load()
    episode_guid="https://nutritionfacts.org/?post_type=audio&p=64971"
    assert db.find_by_id(episode_guid)

    


        


    
