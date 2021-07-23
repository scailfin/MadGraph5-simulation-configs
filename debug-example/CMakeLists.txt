add_executable(drell-yan_example "drell-yan_example.cxx")

target_link_libraries(drell-yan_example momemta::momemta)
# FIXME: The TTbar example uses TreePlayer so copy this here FOR NOW
target_link_libraries(drell-yan_example ${ROOT_TREEPLAYER_LIBRARY})

set_target_properties(drell-yan_example
      PROPERTIES
      OUTPUT_NAME "drell-yan_example.exe")
