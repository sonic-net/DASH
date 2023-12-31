#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdint.h>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#define MODEL_PORT 46500
#define MODEL_IP "127.0.0.1"

static int _model_socket;

int model_api_init() {
    struct sockaddr_in serv_addr;
    if ((_model_socket = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cout<<"Could not create socket"<<std::endl;
        return -1;
    }
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(MODEL_PORT);
    inet_pton(AF_INET, MODEL_IP, &serv_addr.sin_addr);
    if (connect(_model_socket, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cout<<"Could not connect to server"<<std::endl;
        return -1;
    }
    return 0;
}

void model_api_deinit() {
    close(_model_socket);
}

class InsertRequest {
public:
    class Value {
    public:
        class Ternary {
        public:
            std::string value;
            std::string mask;
        };
        class LPM {
        public:
            std::string value;
            int prefix_len;
        };
        class Range {
        public:
            std::string first;
            std::string last;
        };

        std::string exact;
        Ternary ternary;
        LPM prefix;
        Range range;
        std::vector<Ternary> ternary_list;
        std::vector<Range> range_list;
    };

    int table;
    std::vector<Value> values;
    int action;
    std::vector<std::string> params;
    int priority;

    std::string jsonize() {
        rapidjson::StringBuffer s;
        rapidjson::Writer<rapidjson::StringBuffer> writer(s);

        writer.StartObject();
            writer.Key("table");
            writer.Uint(table);

            writer.Key("values");
            writer.StartArray();
            for (auto & v : values) {
                writer.StartObject();
                    writer.Key("exact");
                    writer.String(v.exact.c_str());

                    writer.Key("ternary");
                    writer.StartObject();
                        writer.Key("value");
                        writer.String(v.ternary.value.c_str());

                        writer.Key("mask");
                        writer.String(v.ternary.mask.c_str());
                    writer.EndObject();

                    writer.Key("prefix");
                    writer.StartObject();
                        writer.Key("value");
                        writer.String(v.prefix.value.c_str());

                        writer.Key("prefix_len");
                        writer.Uint(v.prefix.prefix_len);
                    writer.EndObject();

                    writer.Key("range");
                    writer.StartObject();
                        writer.Key("first");
                        writer.String(v.range.first.c_str());

                        writer.Key("last");
                        writer.String(v.range.last.c_str());
                    writer.EndObject();

                    writer.Key("ternary_list");
                    writer.StartArray();
                    for (auto & item : v.ternary_list) {
                        writer.StartObject();
                            writer.Key("value");
                            writer.String(item.value.c_str());

                            writer.Key("mask");
                            writer.String(item.mask.c_str());
                        writer.EndObject();
                    }
                    writer.EndArray();

                    writer.Key("range_list");
                    writer.StartArray();
                    for (auto & item : v.range_list) {
                        writer.StartObject();
                            writer.Key("first");
                            writer.String(item.first.c_str());

                            writer.Key("last");
                            writer.String(item.last.c_str());
                        writer.EndObject();
                    }
                    writer.EndArray();
                writer.EndObject();
            }
            writer.EndArray();

            writer.Key("action");
            writer.Uint(action);

            writer.Key("params");
            writer.StartArray();
            for (auto & p : params) {
                writer.String(p.c_str());
            }
            writer.EndArray();

            writer.Key("priority");
            writer.Uint(priority);
        writer.EndObject();

        const char * buf = s.GetString();
        int buf_size = s.GetSize();
        return std::string(buf, buf_size);
    }
};

void model_api_insert(InsertRequest& insertRequest) {
    uint8_t api_id = 0;
    uint32_t json_buf_size;
    const char *json_buf;
    char json_buf_size_cstr[16];
    bool status;

    send(_model_socket, &api_id, sizeof(uint8_t), 0);

    std::string json_repr = insertRequest.jsonize();
    json_buf = json_repr.c_str();
    json_buf_size = strlen(json_buf);

    snprintf(json_buf_size_cstr, 16, "%08X", json_buf_size);
    send(_model_socket, json_buf_size_cstr, 8, 0);

    send(_model_socket, json_buf, json_buf_size, 0);

    read(_model_socket, &status, 1);
}


/*
vip.insert({
    "hdr.ipv4.dst_addr" : 0xC0A80A0F,
    "action"            : accept,
    "params"            : []
})
*/
int main()
{
    if (model_api_init() < 0) {
        return -1;
    }

    InsertRequest insertRequest;
    insertRequest.table = 19;
    InsertRequest::Value vip_hdr_ipv4_dst_addr;
    vip_hdr_ipv4_dst_addr.exact = std::string("0xC0A80A0F");
    insertRequest.values.push_back(vip_hdr_ipv4_dst_addr);
    insertRequest.action = 20;
    model_api_insert(insertRequest);

    model_api_deinit();
    return 0;
}
