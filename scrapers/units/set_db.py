
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from pymongo import MongoClient
from bson.code import Code
from units.set_log import LOG


logging = LOG(log_file_name="set_db")


def max_id(person):
    # max id
    doc_id = [int(doc["id"]) for doc in person.find({}, {"id": 1}).sort([('id', -1)]).limit(1)]
    if not doc_id:
        doc_id = [0]
    return doc_id[0] + 1


def connect_mongodb():
    client = MongoClient('localhost', 27017)
    db = client['degirmen_face']
    return {'client': client, 'db': db}


# def connect_db():
#     client = MongoClient('10.2.6.39', 27017)
#     db = client["ssm"]
#     db_username = "nesij"
#     db_password = "dmXU4vb"
#     db.authenticate(db_username, db_password)
#
#     return {"db": db, "client": client}


# if(value <= 0.5)
def map_face_retinaface():
    return Code("""
                    function() {
                        var input = embed;

                        var value = Array.sum(this.face_embed.map(function(el,idx) {
                                                var mul = Math.abs(el - input[idx]);
                                                return mul * mul;
                                    }));
                        value = Math.sqrt(value)
                        /*
                        value = Math.sqrt(value) - 0.5;
                        if (value < 0) value = 0;
                        else if (value > 1) value = 1;
                        */
                        if(value <= 1.0) 
                            emit(this._id, {"user_id":this.user_id,
                                            "tc_number":this.tc_number,
                                            "name":this.name,
                                            "surname":this.surname,
                                            "gender":this.gender,
                                            "image_path":this.image_path,
                                            "score": value });

                    }
           """)


def reduce_face():
    return Code("""
                    function(key, values) {
                        var output = [];

                        values.forEach(function(value) {
                            value.output.forEach(function(item) {
                                output.push(item);
                            });
                        });
                        return { "output": output};
                    }
           """)
