"""
source.py
Source object for GALFACTS transiet search
04 June 2014 - Trey Wenger - creation
11 June 2014 - Joseph Kania - Modification
10 July 2014 - Trey Wenger - plots both all data and data used for
                             fit
"""
import sys
import numpy as np
import make_plots
from scipy.optimize import curve_fit

class Source(object):
    """Source object for GALFACTS transient search"""
    def __init__(self, RA, DEC, AST, I_data, Q_data, U_data, V_data,
                 all_RA, all_DEC, all_AST, all_I_data,all_Q_data,
                 all_U_data,all_V_data,
                 time_end, dec_end):
        """Initialize the source object"""
        self.RA = RA
        self.DEC = DEC
        self.AST = AST
        self.I_data = I_data
        self.Q_data = Q_data
        self.U_data = U_data
        self.V_data = V_data
        self.all_RA = all_RA
        self.all_DEC = all_DEC
        self.all_AST = all_AST
        self.all_I_data = all_I_data
        self.all_Q_data = all_Q_data
        self.all_U_data = all_U_data
        self.all_V_data = all_V_data
        self.time_end = time_end
        self.dec_end = dec_end
        self.fit_p = None
        self.e_fit_p = None
        self.good_fit = None
        self.center_RA = RA[len(RA)/2]
        self.center_DEC = DEC[len(DEC)/2]
        self.I_baselined = None
        self.center_I = None
        self.bad_reasons = ""

    def fit(self, filename, **options):
        """Fit the source I data vs. DEC with a Gaussian +
           linear baseline"""
        # middle of data
        mid = len(self.I_data) / 2
        # line guess
        slope_guess = (self.I_data[-1] - self.I_data[0])/(self.DEC[-1] -
                                                          self.DEC[0])
        y_int_guess = self.I_data[0] - slope_guess*self.DEC[0]
        constant_guess = np.mean(self.I_data)
        # gaussian guess
        amp_guess = self.I_data[mid] - (slope_guess*self.DEC[mid]+y_int_guess)
        center_guess = self.DEC[mid]
        # width in dec
        sigma_guess = np.abs(self.DEC[mid+3] - center_guess)
        # fill the structure
        #guess_p = [amp_guess, center_guess, sigma_guess, y_int_guess,
        #           slope_guess]
        guess_p = [amp_guess, center_guess, sigma_guess, constant_guess ,slope_guess, 0.5, 0.5]
        sigma = [options["sigma"]]*len(self.DEC)
        try:
            fit_p, covar = curve_fit(gauss_and_poly,  self.DEC,
                                     self.I_data, p0=guess_p,
                                     sigma=sigma)
            print("fit_p is {0}".format(fit_p))
        except RuntimeError:
            if options["verbose"]:
                print("Log: A fit did not converge.")
            self.good_fit = False
            self.bad_reasons+="fit_no_converge,"
            return
            
        self.fit_p = np.array(fit_p)
        self.covar = np.array(covar)
        
        if (np.isinf(fit_p).any() or np.isinf(covar).any() or
            np.isnan(fit_p).any() or np.isnan(covar).any()):
            self.good_fit = False
            self.bad_reasons+="fit_is_nan_or_inf,"
        else:
            self.e_fit_p = np.array([np.sqrt(covar[i,i])
                                 for i in range(len(fit_p))])
            residuals = self.I_data - gauss_and_line(self.DEC,*fit_p)
            #chisq, p = chisquare(gauss_and_line(self.DEC,*fit_p), f_exp=self.I_data)
            dof = len(self.I_data) - len(fit_p) - 1 # degrees of freedom
            chisq = np.sum( ( (self.I_data - gauss_and_line(self.DEC,*fit_p)) / options["sigma"] )**2. )
            reduced_chisq = chisq / dof
            red_chisq_mean = reduced_chisq / np.mean(self.I_data)**2.
            #
            print "I_data"
            print self.I_data
            print "Fit data"
            print gauss_and_line(self.DEC,*fit_p)
            print "Degrees of freedom"
            print len(self.I_data)
            print "Chi-sq"
            print chisq
            print "Reduced chi-sq"
            print reduced_chisq
            print "Reduced chi-sq over mean-sq"
            print red_chisq_mean
            self.bad_reasons+=" red_chisq is {0} ".format(reduced_chisq) #for testing
            if (np.abs(self.e_fit_p[0]/self.fit_p[0])<options["amp_req"] and
                np.abs(self.e_fit_p[2]/self.fit_p[2])<options["width_req"]):
                self.good_fit = True
                #self.good_fit = False #to display chisqr for testing
                # determine center properties by finding closest point
                # to center
                center_point = np.abs(self.DEC - self.fit_p[1]).argmin()
                self.center_RA = self.RA[center_point]
                self.center_DEC = self.DEC[center_point]
                self.I_baselined = (self.I_data -
                                    (self.fit_p[3] +
                                    self.fit_p[4]*self.DEC))
                self.center_I = self.I_baselined[center_point]
                print("center_I is {0}".format(self.center_I))
            else:
                self.good_fit = False
                self.bad_reasons+="bad_fit_uncert,"
            # for plotting
            if options["file_verbose"]:
                if (not self.good_fit or self.dec_end or self.time_end):
                    gb = " - bad fit - "
                else:
                    gb = " - good fit"
                gb += self.bad_reasons
                if self.dec_end :
                    gb += " dec_end"
                elif self.time_end:
                    gb += " time end"
                fit_x = np.linspace(self.DEC[0], self.DEC[-1], 100)
                fit_y = gauss_and_poly(fit_x, *fit_p)
                make_plots.source_plot(self.DEC, self.I_data,
                                       self.all_DEC,self.all_I_data,
                                       residuals,
                                       fit_x, fit_y, filename, gb)
            
"""
def gauss_and_line(x, *p):
    amp, center, sigma, y_int, slope = p
    return y_int + slope*x + amp*np.exp(-(x-center)**2/(2.*sigma**2))
    #amp,center,sigma,coeff0,coeff1,coeff2,coeff3 = p
    #return (coeff0 + coeff1*x + coeff2*x**2. + coeff3*x**3. +
    #        amp*np.exp(-(x-center)**2/(2.*sigma**2)))
"""
def gauss_and_poly(x, *p):
    amp, center, sigma, coeff0, coeff1, coeff2, coeff3 = p
    return (coeff0 + coeff1*x + coeff2*x**2.0 + coeff3*x**3.0 +
            amp*np.exp(-(x-center)**2/(2.0*sigma**2)))

if __name__ == "__main__":
    sys.exit("Error: module not meant to be run from top level")
