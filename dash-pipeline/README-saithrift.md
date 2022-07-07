                 ^~~~
ar rcs ./obj/librpcserver.a obj/sai_rpc.o obj/sai_types.o obj/sai_rpc_server.o
g++ -I/usr/include/sai -I. -std=c++11 -O0 -ggdb -c src/saiserver.cpp  -o obj/saiserver.o -I/usr/include/sai -I. -std=c++11 -O0 -ggdb -DBRCMSAI -I./gen-cpp -I../../inc
g++ -L/usr/lib -Wl,-rpath=/usr/lib ./obj/sai_rpc_server.o ./obj/saiserver.o -o saiserver \
	   ./obj/librpcserver.a -lthrift -lpthread -lsai
./obj/sai_rpc_server.o: In function `convert_attr_thrift_to_sai(_sai_object_type_t, sai::sai_thrift_attribute_t const&, _sai_attribute_t*)':
/dash/dash-pipeline/SAI/SAI/test/saithriftv2/../../meta/sai_rpc_frontend.cpp:132: undefined reference to `sai_metadata_get_attr_metadata'
./obj/sai_rpc_server.o: In function `convert_attr_sai_to_thrift(_sai_object_type_t, _sai_attribute_t const&, sai::sai_thrift_attribute_t&)':
/dash/dash-pipeline/SAI/SAI/test/saithriftv2/../../meta/sai_rpc_frontend.cpp:554: undefined reference to `sai_metadata_get_attr_metadata'
/usr/lib/libsai.so: undefined reference to `p4::v1::MasterArbitrationUpdate* google::protobuf::Arena::CreateMaybeMessage<p4::v1::MasterArbitrationUpdate>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::MessageLite::SerializeToZeroCopyStream(google::protobuf::io::ZeroCopyOutputStream*) const'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageRequest::clear_update()'
/usr/lib/libsai.so: undefined reference to `p4::config::v1::P4Info::P4Info(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::TextFormat::Parse(google::protobuf::io::ZeroCopyInputStream*, google::protobuf::Message*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::ZeroFieldsBase::~ZeroFieldsBase()'
/usr/lib/libsai.so: undefined reference to `p4::v1::SetForwardingPipelineConfigRequest::SetForwardingPipelineConfigRequest(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Uint128* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Uint128>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::P4Runtime::Stub::async'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::IstreamInputStream::CopyingIstreamInputStream::~CopyingIstreamInputStream()'
/usr/lib/libsai.so: undefined reference to `grpc::ClientContext::ClientContext()'
/usr/lib/libsai.so: undefined reference to `p4::v1::WriteRequest::~WriteRequest()'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableAction::clear_type()'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::P4Runtime::Stub'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableEntry::TableEntry(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Action_Param* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Action_Param>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Entity::set_allocated_table_entry(p4::v1::TableEntry*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::WriteResponse::WriteResponse(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `grpc::InsecureChannelCredentials()'
/usr/lib/libsai.so: undefined reference to `google::rpc::_Status_default_instance_'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageRequest::StreamMessageRequest(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::Message::ShortDebugString[abi:cxx11]() const'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::ArenaStringPtr::Mutable[abi:cxx11](google::protobuf::internal::ArenaStringPtr::EmptyDefault, google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Update* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Update>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::WriteResponse'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::CopyingInputStreamAdaptor::~CopyingInputStreamAdaptor()'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::Stub::StreamChannelRaw(grpc::ClientContext*)'
/usr/lib/libsai.so: undefined reference to `grpc::g_core_codegen_interface'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch* google::protobuf::Arena::CreateMaybeMessage<p4::v1::FieldMatch>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::WriteRequest::WriteRequest(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch_LPM* google::protobuf::Arena::CreateMaybeMessage<p4::v1::FieldMatch_LPM>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageResponse::~StreamMessageResponse()'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::RepeatedPtrFieldBase::AddOutOfLineHelper(void*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::_MasterArbitrationUpdate_default_instance_'
/usr/lib/libsai.so: undefined reference to `vtable for google::protobuf::io::ZeroCopyOutputStream'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableAction* google::protobuf::Arena::CreateMaybeMessage<p4::v1::TableAction>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableEntry::~TableEntry()'
/usr/lib/libsai.so: undefined reference to `grpc::ClientContext::~ClientContext()'
/usr/lib/libsai.so: undefined reference to `google::protobuf::MessageLite::ParseFromZeroCopyStream(google::protobuf::io::ZeroCopyInputStream*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::GetOwnedMessageInternal(google::protobuf::Arena*, google::protobuf::MessageLite*, google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::MessageLite::SerializeWithCachedSizesToArray(unsigned char*) const'
/usr/lib/libsai.so: undefined reference to `p4::config::v1::P4Info::~P4Info()'
/usr/lib/libsai.so: undefined reference to `p4::v1::SetForwardingPipelineConfigResponse::SetForwardingPipelineConfigResponse(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Action* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Action>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `absl::lts_20211102::Mutex::~Mutex()'
/usr/lib/libsai.so: undefined reference to `vtable for google::protobuf::io::IstreamInputStream'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageResponse::StreamMessageResponse(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::SetForwardingPipelineConfigResponse'
/usr/lib/libsai.so: undefined reference to `p4::v1::SetForwardingPipelineConfigRequest::~SetForwardingPipelineConfigRequest()'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageRequest::~StreamMessageRequest()'
/usr/lib/libsai.so: undefined reference to `grpc::g_glip'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::Stub::Write(grpc::ClientContext*, p4::v1::WriteRequest const&, p4::v1::WriteResponse*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Entity* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Entity>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::ForwardingPipelineConfig* google::protobuf::Arena::CreateMaybeMessage<p4::v1::ForwardingPipelineConfig>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch::clear_field_match_type()'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::ArenaStringPtr::Set(google::protobuf::internal::ArenaStringPtr::EmptyDefault, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `grpc::CreateChannel(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::shared_ptr<grpc::ChannelCredentials> const&)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::DuplicateIfNonNullInternal(google::protobuf::MessageLite*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::Stub::SetForwardingPipelineConfig(grpc::ClientContext*, p4::v1::SetForwardingPipelineConfigRequest const&, p4::v1::SetForwardingPipelineConfigResponse*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::IstreamInputStream::IstreamInputStream(std::istream*, int)'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch_Exact* google::protobuf::Arena::CreateMaybeMessage<p4::v1::FieldMatch_Exact>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::ZeroCopyOutputStream::WriteAliasedRaw(void const*, int)'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::NewStub(std::shared_ptr<grpc::ChannelInterface> const&, grpc::StubOptions const&)'
/usr/lib/libsai.so: undefined reference to `typeinfo for google::protobuf::io::ZeroCopyOutputStream'
collect2: error: ld returned 1 exit status
Makefile:100: recipe for target 'saiserver' failed
make[2]: *** [saiserver] Error 1
make[2]: Leaving directory '/dash/dash-pipeline/SAI/SAI/test/saithriftv2'
make[1]: *** [saithrift-build] Error 2
Makefile:43: recipe for target 'saithrift-build' failed
make[1]: Leaving directory '/dash/dash-pipeline/SAI/SAI'
Makefile:12: recipe for target 'sai-thrift-server' failed
make: *** [sai-thrift-server] Error 2
make: *** [Makefile:151: sai-thrift-server] Error 2
chris@chris-z4:~/chris-DASH/DASH/dash-pipeline$ 
# sai-thrift-server

                 ^~~~
ar rcs ./obj/librpcserver.a obj/sai_rpc.o obj/sai_types.o obj/sai_rpc_server.o
g++ -I/usr/include/sai -I. -std=c++11 -O0 -ggdb -c src/saiserver.cpp  -o obj/saiserver.o -I/usr/include/sai -I. -std=c++11 -O0 -ggdb -DBRCMSAI -I./gen-cpp -I../../inc
g++ -L/usr/lib -Wl,-rpath=/usr/lib ./obj/sai_rpc_server.o ./obj/saiserver.o -o saiserver \
	   ./obj/librpcserver.a -lthrift -lpthread -lsai
./obj/sai_rpc_server.o: In function `convert_attr_thrift_to_sai(_sai_object_type_t, sai::sai_thrift_attribute_t const&, _sai_attribute_t*)':
/dash/dash-pipeline/SAI/SAI/test/saithriftv2/../../meta/sai_rpc_frontend.cpp:132: undefined reference to `sai_metadata_get_attr_metadata'
./obj/sai_rpc_server.o: In function `convert_attr_sai_to_thrift(_sai_object_type_t, _sai_attribute_t const&, sai::sai_thrift_attribute_t&)':
/dash/dash-pipeline/SAI/SAI/test/saithriftv2/../../meta/sai_rpc_frontend.cpp:554: undefined reference to `sai_metadata_get_attr_metadata'
/usr/lib/libsai.so: undefined reference to `p4::v1::MasterArbitrationUpdate* google::protobuf::Arena::CreateMaybeMessage<p4::v1::MasterArbitrationUpdate>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::MessageLite::SerializeToZeroCopyStream(google::protobuf::io::ZeroCopyOutputStream*) const'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageRequest::clear_update()'
/usr/lib/libsai.so: undefined reference to `p4::config::v1::P4Info::P4Info(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::TextFormat::Parse(google::protobuf::io::ZeroCopyInputStream*, google::protobuf::Message*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::ZeroFieldsBase::~ZeroFieldsBase()'
/usr/lib/libsai.so: undefined reference to `p4::v1::SetForwardingPipelineConfigRequest::SetForwardingPipelineConfigRequest(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Uint128* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Uint128>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::P4Runtime::Stub::async'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::IstreamInputStream::CopyingIstreamInputStream::~CopyingIstreamInputStream()'
/usr/lib/libsai.so: undefined reference to `grpc::ClientContext::ClientContext()'
/usr/lib/libsai.so: undefined reference to `p4::v1::WriteRequest::~WriteRequest()'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableAction::clear_type()'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::P4Runtime::Stub'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableEntry::TableEntry(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Action_Param* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Action_Param>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Entity::set_allocated_table_entry(p4::v1::TableEntry*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::WriteResponse::WriteResponse(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `grpc::InsecureChannelCredentials()'
/usr/lib/libsai.so: undefined reference to `google::rpc::_Status_default_instance_'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageRequest::StreamMessageRequest(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::Message::ShortDebugString[abi:cxx11]() const'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::ArenaStringPtr::Mutable[abi:cxx11](google::protobuf::internal::ArenaStringPtr::EmptyDefault, google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Update* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Update>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::WriteResponse'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::CopyingInputStreamAdaptor::~CopyingInputStreamAdaptor()'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::Stub::StreamChannelRaw(grpc::ClientContext*)'
/usr/lib/libsai.so: undefined reference to `grpc::g_core_codegen_interface'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch* google::protobuf::Arena::CreateMaybeMessage<p4::v1::FieldMatch>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::WriteRequest::WriteRequest(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch_LPM* google::protobuf::Arena::CreateMaybeMessage<p4::v1::FieldMatch_LPM>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageResponse::~StreamMessageResponse()'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::RepeatedPtrFieldBase::AddOutOfLineHelper(void*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::_MasterArbitrationUpdate_default_instance_'
/usr/lib/libsai.so: undefined reference to `vtable for google::protobuf::io::ZeroCopyOutputStream'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableAction* google::protobuf::Arena::CreateMaybeMessage<p4::v1::TableAction>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::TableEntry::~TableEntry()'
/usr/lib/libsai.so: undefined reference to `grpc::ClientContext::~ClientContext()'
/usr/lib/libsai.so: undefined reference to `google::protobuf::MessageLite::ParseFromZeroCopyStream(google::protobuf::io::ZeroCopyInputStream*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::GetOwnedMessageInternal(google::protobuf::Arena*, google::protobuf::MessageLite*, google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::MessageLite::SerializeWithCachedSizesToArray(unsigned char*) const'
/usr/lib/libsai.so: undefined reference to `p4::config::v1::P4Info::~P4Info()'
/usr/lib/libsai.so: undefined reference to `p4::v1::SetForwardingPipelineConfigResponse::SetForwardingPipelineConfigResponse(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Action* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Action>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `absl::lts_20211102::Mutex::~Mutex()'
/usr/lib/libsai.so: undefined reference to `vtable for google::protobuf::io::IstreamInputStream'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageResponse::StreamMessageResponse(google::protobuf::Arena*, bool)'
/usr/lib/libsai.so: undefined reference to `vtable for p4::v1::SetForwardingPipelineConfigResponse'
/usr/lib/libsai.so: undefined reference to `p4::v1::SetForwardingPipelineConfigRequest::~SetForwardingPipelineConfigRequest()'
/usr/lib/libsai.so: undefined reference to `p4::v1::StreamMessageRequest::~StreamMessageRequest()'
/usr/lib/libsai.so: undefined reference to `grpc::g_glip'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::Stub::Write(grpc::ClientContext*, p4::v1::WriteRequest const&, p4::v1::WriteResponse*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::Entity* google::protobuf::Arena::CreateMaybeMessage<p4::v1::Entity>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::ForwardingPipelineConfig* google::protobuf::Arena::CreateMaybeMessage<p4::v1::ForwardingPipelineConfig>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch::clear_field_match_type()'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::ArenaStringPtr::Set(google::protobuf::internal::ArenaStringPtr::EmptyDefault, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `grpc::CreateChannel(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::shared_ptr<grpc::ChannelCredentials> const&)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::internal::DuplicateIfNonNullInternal(google::protobuf::MessageLite*)'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::Stub::SetForwardingPipelineConfig(grpc::ClientContext*, p4::v1::SetForwardingPipelineConfigRequest const&, p4::v1::SetForwardingPipelineConfigResponse*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::IstreamInputStream::IstreamInputStream(std::istream*, int)'
/usr/lib/libsai.so: undefined reference to `p4::v1::FieldMatch_Exact* google::protobuf::Arena::CreateMaybeMessage<p4::v1::FieldMatch_Exact>(google::protobuf::Arena*)'
/usr/lib/libsai.so: undefined reference to `google::protobuf::io::ZeroCopyOutputStream::WriteAliasedRaw(void const*, int)'
/usr/lib/libsai.so: undefined reference to `p4::v1::P4Runtime::NewStub(std::shared_ptr<grpc::ChannelInterface> const&, grpc::StubOptions const&)'
/usr/lib/libsai.so: undefined reference to `typeinfo for google::protobuf::io::ZeroCopyOutputStream'
collect2: error: ld returned 1 exit status
Makefile:100: recipe for target 'saiserver' failed
make[2]: *** [saiserver] Error 1
make[2]: Leaving directory '/dash/dash-pipeline/SAI/SAI/test/saithriftv2'
make[1]: *** [saithrift-build] Error 2
Makefile:43: recipe for target 'saithrift-build' failed
make[1]: Leaving directory '/dash/dash-pipeline/SAI/SAI'
Makefile:12: recipe for target 'sai-thrift-server' failed
make: *** [sai-thrift-server] Error 2
make: *** [Makefile:151: sai-thrift-server] Error 2
chris@chris-z4:~/chris-DASH/DASH/dash-pipeline$ 
