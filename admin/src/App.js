import React from 'react';

class App extends React.Component {
  render(){
    return (
      <main className="main">
    <div className="page-loader">
      <div className="page-loader__spinner">
        <svg viewBox="25 25 50 50">
          <circle cx={50} cy={50} r={20} fill="none" strokeWidth={2} strokeMiterlimit={10} />
        </svg>
      </div>
    </div>
    <section className="content">
      <header className="content__title">
        <h1>Dashboard</h1>
      </header>
      <div className="row quick-stats">
        <div className="col-sm-6 col-md-3">
          <div className="quick-stats__item">
            <div className="quick-stats__info">
              <h2>987,459</h2>
              <small>Total Leads Recieved</small>
            </div>
            <div className="quick-stats__chart peity-bar">6,4,8,6,5,6,7,8,3,5,9</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="quick-stats__item">
            <div className="quick-stats__info">
              <h2>356,785K</h2>
              <small>Total Website Clicks</small>
            </div>
            <div className="quick-stats__chart peity-bar">4,7,6,2,5,3,8,6,6,4,8</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="quick-stats__item">
            <div className="quick-stats__info">
              <h2>$58,778</h2>
              <small>Total Sales Orders</small>
            </div>
            <div className="quick-stats__chart peity-bar">9,4,6,5,6,4,5,7,9,3,6</div>
          </div>
        </div>
        <div className="col-sm-6 col-md-3">
          <div className="quick-stats__item">
            <div className="quick-stats__info">
              <h2>214</h2>
              <small>Total Support Tickets</small>
            </div>
            <div className="quick-stats__chart peity-bar">5,6,3,9,7,5,4,6,5,6,4</div>
          </div>
        </div>
      </div>



      <div className="row">
      <div className="col-lg-12">
      <div class="card">
                    <div class="card-body">
                        <h4 class="card-title">Coaches</h4>

                        <div class="table-responsive">
                            <table id="data-table" class="table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Position</th>
                                        <th>Office</th>
                                        <th>Age</th>
                                        <th>Start date</th>
                                        <th>Salary</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Tiger Nixon</td>
                                        <td>System Architect</td>
                                        <td>Edinburgh</td>
                                        <td>61</td>
                                        <td>2011/04/25</td>
                                        <td>$320,800</td>
                                    </tr>
                                    <tr>
                                        <td>Garrett Winters</td>
                                        <td>Accountant</td>
                                        <td>Tokyo</td>
                                        <td>63</td>
                                        <td>2011/07/25</td>
                                        <td>$170,750</td>
                                    </tr>
                                    <tr>
                                        <td>Ashton Cox</td>
                                        <td>Junior Technical Author</td>
                                        <td>San Francisco</td>
                                        <td>66</td>
                                        <td>2009/01/12</td>
                                        <td>$86,000</td>
                                    </tr>
                                    <tr>
                                        <td>Ashton Cox</td>
                                        <td>Junior Technical Author</td>
                                        <td>San Francisco</td>
                                        <td>66</td>
                                        <td>2009/01/12</td>
                                        <td>$86,000</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                </div>
                </div>

                <div className="row">
      <div className="col-lg-12">
      <div class="card">
                    <div class="card-body">
                        <h4 class="card-title">Users</h4>

                        <div class="table-responsive">
                            <table id="data-table" class="table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Position</th>
                                        <th>Office</th>
                                        <th>Age</th>
                                        <th>Start date</th>
                                        <th>Salary</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Tiger Nixon</td>
                                        <td>System Architect</td>
                                        <td>Edinburgh</td>
                                        <td>61</td>
                                        <td>2011/04/25</td>
                                        <td>$320,800</td>
                                    </tr>
                                    <tr>
                                        <td>Garrett Winters</td>
                                        <td>Accountant</td>
                                        <td>Tokyo</td>
                                        <td>63</td>
                                        <td>2011/07/25</td>
                                        <td>$170,750</td>
                                    </tr>
                                    <tr>
                                        <td>Ashton Cox</td>
                                        <td>Junior Technical Author</td>
                                        <td>San Francisco</td>
                                        <td>66</td>
                                        <td>2009/01/12</td>
                                        <td>$86,000</td>
                                    </tr>
                                    <tr>
                                        <td>Ashton Cox</td>
                                        <td>Junior Technical Author</td>
                                        <td>San Francisco</td>
                                        <td>66</td>
                                        <td>2009/01/12</td>
                                        <td>$86,000</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                </div>
                </div>


                <div className="row">
      <div className="col-lg-6">
                <div class="card widget-pie">
                        <div class="col-6 col-sm-4 col-md-6 col-lg-4 widget-pie__item">
                           
                            <div class="widget-pie__title">Email<br/> Scheduled</div>
                        </div>

                        <div class="col-6 col-sm-4 col-md-6 col-lg-4 widget-pie__item">
                         
                            <div class="widget-pie__title">Email<br/> Bounced</div>
                        </div>

                        <div class="col-6 col-sm-4 col-md-6 col-lg-4 widget-pie__item">
                           
                            <div class="widget-pie__title">Email<br/> Opened</div>
                        </div>

                        <div class="col-6 col-sm-4 col-md-6 col-lg-4 widget-pie__item">
                        
                            <div class="widget-pie__title">Storage<br/>Remaining</div>
                        </div>

                        <div class="col-6 col-sm-4 col-md-6 col-lg-4 widget-pie__item">
                         
                            <div class="widget-pie__title">Web Page<br/> Views</div>
                        </div>

                        <div class="col-6 col-sm-4 col-md-6 col-lg-4 widget-pie__item">
                          
                            <div class="widget-pie__title">Server<br/> Processing</div>
                        </div>
                    </div>
                    </div>
                    </div>
                
      <footer className="footer hidden-xs-down">
      </footer>
    </section>
  </main>
    )
  }
}

export default App;
