task :tags do
  sh "etags `ls *py`"
end

task :test => :tags do
  sh "python -m unittest discover -p '*test*.py'"
end

task :report => :test do
  sh "python Application.py --verbose --debug --localrss --report"
end

task  :wbur => :test do
  sh "python Application.py --verbose --debug --localrss --program=wbur"
end

task :all => [ :test, :report ] do

end
