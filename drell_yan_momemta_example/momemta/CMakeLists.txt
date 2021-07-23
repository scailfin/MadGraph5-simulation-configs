add_executable(drell_yan "drell_yan.cxx")

target_link_libraries(drell_yan momemta::momemta)

set_target_properties(drell_yan PROPERTIES OUTPUT_NAME "drell_yan.exe")
