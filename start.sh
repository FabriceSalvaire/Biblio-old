####################################################################################################
#
# How to Start
#
####################################################################################################

# Set the environment
. setenv.sh 

# PyQt
cd Babel/GUI/ui
make -f Makefile.pyqt
cd -

# Build
python setup.py build

# Update TAGS file
./tools/update-tags 

# Generate RST files
##./tools/generate-rst 
# Generate HTML Documentation
# cd sphinx/
##./make-html --clean

####################################################################################################
#
# End
#
####################################################################################################