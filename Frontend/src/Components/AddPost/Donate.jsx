import React, { Component, useEffect } from "react";
import { useState } from "react";
import { Button, Grid, TextField } from "@material-ui/core";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import OfflineBoltIcon from "@material-ui/icons/OfflineBolt";
import Box from "@material-ui/core/Box";
import { Breakpoint } from "react-socks";
import Divider from "@material-ui/core/Divider";
import AddIcon from "@material-ui/icons/Add";
import CancelRoundedIcon from "@material-ui/icons/CancelRounded";
import { Request, RequestImg } from "../../api/Request";
import {
	FormLabel,
	FormControl,
	Radio,
	FormControlLabel,
	FormGroup,
	RadioGroup,
} from "@material-ui/core";
import { CreateNewPost, CreatePostSuccess } from "../../redux/post/postActions";
import { connect } from "react-redux";
import { getCategories, getColors } from "../../helper";
import { plugToRequest } from "react-cookies";
import { withRouter } from "react-router-dom";

class Donate extends Component {
	constructor(props) {
		super(props);

		this.state = {
			category: "",
			subcategory: "",
			color: "",
			condn: "",
			title: "",
			desc: "",
			brand: "",
			premium: "false",
			loading: false,
			price: "",
			formValid: false,
			categoryValid: false,
			fieldValid: {
				category: false,
				subcategory: false,
				color: false,
				condn: false,
				title: false,
				desc: false,
				brand: false,
				price: false,
			},
			img1: { image: null, file: null },
			img2: { image: null, file: null },
			img3: { image: null, file: null },
			img4: { image: null, file: null },
		};
	}

	async componentDidMount() {
		await this.props.setInitialDispatch(false, null);
	}

	onHandleChange = async (event) => {
		event.preventDefault();
		const name = event.target.name;
		const value = event.target.value;
		await this.setState({ ...this.state, [name]: value }, () =>
			this.validateField(name, value)
		);
	};

	validateField = async (fieldName, value) => {
		let val = false;
		switch (fieldName) {
			case "category":
				value == "" ? (val = false) : (val = true);
				break;
			case "subcategory":
				value == "" ? (val = false) : (val = true);
				break;
			case "color":
				value == "" ? (val = false) : (val = true);
				break;
			case "condn":
				value == "" ? (val = false) : (val = true);
				break;
			case "brand":
				value == "" ? (val = false) : (val = true);
				break;
			case "title":
				value.length <= 2 || value.length >= 100 ? (val = false) : (val = true);
				break;
			case "desc":
				value.length <= 5 || value.length > 250 ? (val = false) : (val = true);
				break;
			default:
				break;
		}
		await this.setState({
			fieldValid: { ...this.state.fieldValid, [fieldName]: val },
		});
		this.validateForm();
	};

	validateForm = async () => {
		// console.log(
		//   this.state.fieldValid["category"] && this.state.fieldValid["subcategory"]
		// );
		await this.setState({
			formValid:
				this.state.fieldValid["category"] &&
				this.state.fieldValid["subcategory"] &&
				this.state.fieldValid["brand"] & this.state.fieldValid["color"] &&
				this.state.fieldValid["title"] &&
				this.state.fieldValid["desc"] &&
				this.state.fieldValid["condn"] &&
				(this.state.img1.image ||
					this.state.img2.image ||
					this.state.img3.image ||
					this.state.img4.image),
		});
	};

	onImageChange = async (e) => {
		const name = e.target.name;
		if (name == "img1")
			await this.setState(
				{
					img1: {
						image: URL.createObjectURL(e.target.files[0]),
						file: e.target.files[0],
					},
				},
				this.validateForm
			);
		else if (name == "img2")
			await this.setState(
				{
					img2: {
						image: URL.createObjectURL(e.target.files[0]),
						file: e.target.files[0],
					},
				},
				this.validateForm
			);
		else if (name == "img3")
			await this.setState(
				{
					img3: {
						image: URL.createObjectURL(e.target.files[0]),
						file: e.target.files[0],
					},
				},
				this.validateForm
			);
		else if (name == "img4")
			await this.setState(
				{
					img4: {
						image: URL.createObjectURL(e.target.files[0]),
						file: e.target.files[0],
					},
				},
				this.validateForm
			);
	};

	onHandleSubmit = async () => {
		const data = new FormData();
		data.append("img1", this.state.img1.file);
		data.append("img2", this.state.img2.file);
		data.append("img3", this.state.img3.file);
		data.append("img4", this.state.img4.file);
		data.append("category", this.state.category);
		data.append("subcategory", this.state.subcategory);
		data.append("color", this.state.color);
		data.append("condition", this.state.condn);
		data.append("title", this.state.title);
		data.append("description", this.state.desc);
		data.append("brand", this.state.brand);
		data.append("is_premium", this.state.premium);
		data.append("price", 0);
		data.append("is_barter", false);
		data.append("is_donate", true);
		await this.props.createPost(data);
	};

	render() {
		const categories = getCategories();
		const colors = getColors();
		if (this.props.success) {
			this.props.history.push(`/donate/${this.props.postId}`);
			return null;
		}

		return (
			<React.Fragment>
				<div className="outer1">
					<div className="outer1__headings">
						<h1>Donate your Product</h1>
						<h3>
							Hi, <span>{this.props.myDetails.username}</span>
						</h3>
					</div>
					<Grid container className="outer1__sell">
						<Grid
							item
							lg={7}
							md={7}
							sm={12}
							xs={12}
							className="outer1__sell__lt"
						>
							<div className="outer1__sell__lt__heading1">
								<div style={{ color: "#ffef00", padding: "6px 8px" }}>
									<OfflineBoltIcon />
								</div>
								<h3>Post ad to earn 50 Trade-coin in your account</h3>
							</div>
							<form className="outer1__sell__lt">
								<Grid container className="outer1__sell__lt__outer">
									<Grid
										lg={6}
										md={6}
										sm={12}
										xs={12}
										style={{ paddingRight: "4px" }}
										className="outer__sell__lt__outer__categ"
									>
										<div className="login__right__myForm__formData">
											<label htmlFor="name">Category</label>
											<br />
											<Box style={{ paddingTop: "10px" }}>
												<Select
													id="demo-simple-select"
													value={this.state["category"]}
													displayEmpty
													name="category"
													className="login__right__myForm__formData__select"
													variant="outlined"
													// label="Category"
													onChange={this.onHandleChange}
												>
													<MenuItem value="" disabled>
														Select
													</MenuItem>
													{Object.keys(categories).map((item) => (
														<MenuItem value={item}>{item}</MenuItem>
													))}
												</Select>
											</Box>
										</div>
									</Grid>
									<Grid
										item
										lg={6}
										md={6}
										sm={12}
										xs={12}
										style={{ paddingLeft: "4px" }}
										className="outer1__sell_lt__outer__subcate"
									>
										<div className="login__right__myForm__formData">
											<label htmlFor="name">Sub-Category</label>
											<br />
											<Box
												sx={{ minWidth: 120 }}
												style={{ paddingTop: "10px" }}
											>
												<Select
													id="demo-simple-select"
													value={this.state["subcategory"]}
													displayEmpty
													variant="outlined"
													disabled={this.state["category"] == ""}
													name="subcategory"
													className="login__right__myForm__formData__select"
													onChange={this.onHandleChange}
												>
													<MenuItem value="" disabled>
														Select
													</MenuItem>
													{this.state.category != "" &&
														categories[this.state.category].map((item) => (
															<MenuItem value={item}>{item}</MenuItem>
														))}
												</Select>
											</Box>
										</div>
									</Grid>
								</Grid>

								<Grid container className="outer1__sell__lt__outer">
									<Grid
										lg={6}
										md={6}
										sm={12}
										xs={12}
										style={{ paddingRight: "4px" }}
										className="outer1__sell__lt__outer__categ"
									>
										<div className="login__right__myForm__formData">
											<label htmlFor="name">Color</label>
											<br />
											<Box
												sx={{ minWidth: 200 }}
												style={{ paddingTop: "10px" }}
											>
												<Select
													id="demo-simple-select"
													value={this.state["color"]}
													displayEmpty
													variant="outlined"
													name="color"
													className="login__right__myForm__formData__select"
													style={{ backgroundColor: "white" }}
													onChange={this.onHandleChange}
												>
													<MenuItem value="" disabled>
														Select
													</MenuItem>
													{colors.map((item) => (
														<MenuItem value={item}>{item}</MenuItem>
													))}
												</Select>
											</Box>
										</div>
									</Grid>
									<Grid
										lg={6}
										md={6}
										sm={12}
										xs={12}
										className="outer1__sell_lt__outer__subcate"
									>
										<div
											className="outer1__sell__lt__outer__brand"
											style={{ width: "100%" }}
										>
											<div className="login__right__myForm__formData">
												<label htmlFor="name">Brand</label>
												<br />
												<TextField
													onChange={this.onHandleChange}
													required
													style={{ paddingTop: "10px", width: "100%" }}
													// className="login__right__myForm__formData__username"
													name="brand"
													value={this.state["value"]}
													placeholder="Brand"
													variant="outlined"
													className="login__right__myForm__formData__select"
												></TextField>
											</div>
										</div>
									</Grid>
								</Grid>

								<Grid container className="outer1__sell__lt__outer">
									<Grid
										lg={6}
										md={6}
										sm={12}
										xs={12}
										className="outer1__sell__lt__outer__categ"
										style={{ width: "100%", paddingRight: "4px" }}
									>
										<div className="login__right__myForm__formData">
											<label htmlFor="name">Condition</label>
											<br />
											<Box style={{ paddingTop: "10px" }}>
												<Select
													id="demo-simple-select"
													value={this.state["condn"]}
													name="condn"
													displayEmpty
													variant="outlined"
													className="login__right__myForm__formData__select"
													onChange={this.onHandleChange}
												>
													<MenuItem value="" disabled>
														Select
													</MenuItem>
													<MenuItem value="Good">Good</MenuItem>
													<MenuItem value="New">New</MenuItem>
													<MenuItem value="Like new">Like new</MenuItem>
													<MenuItem value="Fair">Fair</MenuItem>
													<MenuItem value="Poor">Poor</MenuItem>
												</Select>
											</Box>
										</div>
									</Grid>
									{/* <Grid
                  lg={6}
                  md={6}
                  sm={12}
                  xs={12}
                  style={{ paddingLeft: "4px" }}
                  className="outer1__sell__lt__outer__subcate"
                >
                  <div
                    className="login__right__myForm__formData"
                    style={{ width: "100%" }}
                  >
                    <label htmlFor="name">Price</label>
                    <br />
                    <TextField
                      className="outer1__sell__lt__outer__subcate__tf"
                      id="filled-number"
                      placeholder="Range"
                      // type="number"
                      name="price"
                      onChange={this.onHandleChange}
                      value={this.state["price"]}
                      style={{ width: "100%" }}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      variant="outlined"
                    />
                  </div>
                </Grid> */}
								</Grid>

								<div className="login__right__myForm__formData">
									<label htmlFor="name">Title</label>
									<br />
									<TextField
										onChange={this.onHandleChange}
										required
										className="login__right__myForm__formData__username"
										name="title"
										value={this.state["title"]}
										variant="outlined"
									></TextField>
								</div>
								<div className="login__right__myForm__formData">
									<label htmlFor="name">Description</label>
									<br />
									<TextField
										onChange={this.onHandleChange}
										required
										name="desc"
										multiline
										value={this.state["desc"]}
										row={8}
										className="login__right__myForm__formData__username"
										variant="outlined"
									></TextField>
								</div>

								<div className="outer1__sell__lt__img">
									<label
										className="login__right__myForm__formData"
										htmlFor="image"
									>
										Images
									</label>
									<br />
									<p>You can choose upto 4 images</p>
									<div className="outer1__sell__lt__img__sel">
										<div className="outer1__sell__lt__img__sel__bdr">
											<div className="outer1__sell__lt__img__sel__bdr__crc">
												{!this.state.img1.image ? (
													<Button variant="contained" component="label">
														<AddIcon />
														<input
															type="file"
															hidden
															onChange={this.onImageChange}
															name="img1"
															accept="image/png, image/jpeg"
														/>
													</Button>
												) : (
													<>
														<img src={this.state.img1.image} />
														<CancelRoundedIcon
															className="outer1__sell__lt__img__sel__bdr__crc__close"
															onClick={() =>
																this.setState({
																	img1: { image: null, file: null },
																})
															}
														/>
													</>
												)}
											</div>
										</div>
										<div className="outer1__sell__lt__img__sel__bdr">
											<div className="outer1__sell__lt__img__sel__bdr__crc">
												{!this.state.img2.image ? (
													<Button variant="contained" component="label">
														<AddIcon />
														<input
															type="file"
															hidden
															onChange={this.onImageChange}
															name="img2"
															accept="image/png, image/jpeg"
														/>
													</Button>
												) : (
													<>
														<img src={this.state.img2.image} />
														<CancelRoundedIcon
															className="outer1__sell__lt__img__sel__bdr__crc__close"
															onClick={() =>
																this.setState({
																	img2: { image: null, file: null },
																})
															}
														/>
													</>
												)}
											</div>
										</div>
										<div className="outer1__sell__lt__img__sel__bdr">
											<div className="outer1__sell__lt__img__sel__bdr__crc">
												{!this.state.img3.image ? (
													<Button variant="contained" component="label">
														<AddIcon />
														<input
															type="file"
															hidden
															onChange={this.onImageChange}
															name="img3"
															accept="image/png, image/jpeg"
														/>
													</Button>
												) : (
													<>
														<img src={this.state.img3.image} />
														<CancelRoundedIcon
															className="outer1__sell__lt__img__sel__bdr__crc__close"
															onClick={() =>
																this.setState({
																	img3: { image: null, file: null },
																})
															}
														/>
													</>
												)}
											</div>
										</div>
										<div className="outer1__sell__lt__img__sel__bdr">
											<div className="outer1__sell__lt__img__sel__bdr__crc">
												{!this.state.img4.image ? (
													<Button variant="contained" component="label">
														<AddIcon />
														<input
															type="file"
															hidden
															onChange={this.onImageChange}
															name="img4"
															accept="image/png, image/jpeg"
														/>
													</Button>
												) : (
													<>
														<img src={this.state.img4.image} />
														<CancelRoundedIcon
															className="outer1__sell__lt__img__sel__bdr__crc__close"
															onClick={() =>
																this.setState({
																	img4: { image: null, file: null },
																})
															}
														/>
													</>
												)}
											</div>
										</div>
									</div>
								</div>
							</form>
						</Grid>
						<Grid
							item
							lg={5}
							md={5}
							sm={12}
							xs={12}
							className="outer1__sell__rt"
						>
							<div className="outer1__sell__rt__box">
								<div className="outer1__sell__rt__box__coin">
									<div className="outer1__sell__rt__box__coin__icon">
										<OfflineBoltIcon />
									</div>
									<h1>{this.props.myDetails.coins}</h1>
								</div>
								<h2> Trade coin Balance</h2>
							</div>
							<h3>Types of Ads</h3>
							<Grid container className="outer1__sell__rt__radio">
								<Grid
									item
									xs={7}
									lg={8}
									className="outer1__sell__rt__radio__lt1"
								>
									<FormControl component="fieldset">
										<RadioGroup
											name="premium"
											value={this.state.premium}
											onChange={this.onHandleChange}
										>
											<FormControlLabel
												style={{ paddingBottom: "1.4rem" }}
												control={<Radio />}
												label="Free Ad"
												value="false"
											/>
											<div className="outer1__sell__rt__radio__lt1__hr">
												<hr />
											</div>
											<FormControlLabel
												style={{ paddingTop: "1rem" }}
												control={<Radio />}
												label="Premium Ad"
												disabled={this.props.myDetails.coins < 250}
												value="true"
											/>
										</RadioGroup>
									</FormControl>
								</Grid>
								<Grid
									item
									xs={5}
									lg={4}
									className="outer1__sell__rt__radio__rt1"
								>
									<div
										className="outer1__sell__rt__radio__rt1__con"
										style={{ color: "#ffef00", paddingBottom: "1.2rem" }}
									>
										<OfflineBoltIcon />
										<div
											className="outer1__sell__rt__radio__rt1__con__heading3
                  "
										>
											<h4> 0 / Month</h4>
										</div>
									</div>
									<div
										className="outer1__sell__rt__radio__rt1__con"
										style={{ color: "#ffef00", paddingTop: "1.7rem" }}
									>
										<OfflineBoltIcon />
										<div
											className="outer1__sell__rt__radio__rt1__con__heading3
                      
                  "
										>
											<h4> 250 / Month</h4>
										</div>
									</div>
								</Grid>
							</Grid>

							<div className="outer1__sell__rt__more">
								<p>
									- Visible above all regular Ads.
									<br />
									-'Premium' tag
									<br />- Priority in search results.
									<br />- 4 weeks validity as premium
								</p>
							</div>

							<Button
								onClick={this.onHandleSubmit}
								className="login__right__myForm__loginButton"
								type="submit"
								disabled={!this.state.formValid}
							>
								Create Ad
							</Button>
						</Grid>
					</Grid>
				</div>
			</React.Fragment>
		);
	}
}

const mapStateToProps = (state) => {
	return {
		myDetails: state.myDetails.myDetails,
		success: state.post.success,
		postId: state.post.postId,
	};
};

const mapDispatchToProps = (dispatch) => {
	return {
		createPost: (data) => dispatch(CreateNewPost(data)),
		setInitialDispatch: (value, id) => dispatch(CreatePostSuccess(value, id)),
	};
};

export default connect(mapStateToProps, mapDispatchToProps)(withRouter(Donate));
