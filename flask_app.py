from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model
import orm
import repository
import services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


# /allocate Path로 들어오면
@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"],
    )

    try:
        # Service 레이어를 호출한다.
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        # Error 나면 400
        return {"message": str(e)}, 400

    # 그 외에는 201
    return {"batchref": batchref}, 201
