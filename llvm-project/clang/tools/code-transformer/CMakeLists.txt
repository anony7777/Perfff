set(LLVM_LINK_COMPONENTS
  FrontendOpenMP
  Support
  )

add_clang_executable(tran-d-minibatch
  code-transformer.cpp
  )

clang_target_link_libraries(tran-d-minibatch
  PRIVATE
  clangAST
  clangASTMatchers
  clangBasic
  clangFrontend
  clangTooling
  clangToolingRefactoring
  )
